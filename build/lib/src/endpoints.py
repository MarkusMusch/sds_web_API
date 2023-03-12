"""Main module for the FastAPI app

This module contains the FastAPI app and the endpoints for the API.

Functions
----------
    startup
        Initialize the database on start up of the app
    shutdown
        Close the database connection on shutdown of the app
    generate_sample_entry
        Generate an new entry in the database for a sample
    get_samples
        Get all samples from the database
    get_sample_statistics
        Get the statistics for a single sample from the database
"""

import sqlite3

from fastapi import FastAPI
import numpy as np
from scipy.special import gamma

from src.distributions import Distributions, ParameterTypes, Sample, \
                              SampleStatistics


app = FastAPI()


@app.on_event('startup')
async def startup():
    """Initialize the database on start up"""

    # establish a connection with the database
    app.db_connection = None
    try:
        app.db_connection = sqlite3.connect('database/distributions.db')
        app.db_connection.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        raise sqlite3.Error("Failed to establish database connection.") from e

    # create the table for sample definitions if it does not exist yet
    cursor = None
    try:
        cursor = app.db_connection.cursor()
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS sample_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distribution_type TEXT NOT NULL,
                param_one REAL NOT NULL,
                param_two REAL NOT NULL,
                num_samples INTEGER NOT NULL CHECK(num_samples >= 2),
                UNIQUE(distribution_type, param_one, param_two, num_samples)
            )
        """)
        app.db_connection.commit()
    except sqlite3.Error as e:
        app.db_connection.rollback()
        raise sqlite3.Error("Failed to create database table.") from e
    finally:
        if cursor is not None:
            cursor.close()


@app.on_event('shutdown')
async def shutdown():
    """Close the database connection on shutdown"""

    try:
        app.db_connection.close()
    except sqlite3.Error as e:
        raise sqlite3.Error("Failed to close database connection.") from e


@app.post('/sample')
async def generate_sample_entry(sample: Sample):
    """Generate an new entry in the database for a sample

    Parameters
    ----------
    sample : Sample
        The sample to be added to the database

    Returns
    -------
    dict
        The ID of the new entry in the database
    """

    # validate the sample

    if sample.num_samples <= 1:
        raise ValueError("Number of samples must be two or greater")

    if sample.distribution_type == Distributions.uniform:
        if len(sample.params) != 2:
            raise TypeError("Uniform distribution requires exactly two "
                            "parameters")
        if sample.params[0].param_type is not ParameterTypes.min:
            raise TypeError("First parameter must be min")
        if sample.params[1].param_type is not ParameterTypes.max:
            raise TypeError("Second parameter must be max")

    elif sample.distribution_type == Distributions.normal:
        if len(sample.params) != 2:
            raise TypeError("Normal distribution requires exactly two "
                            "parameters")
        if sample.params[0].param_type is not ParameterTypes.mean:
            raise TypeError("First parameter must be mean")
        if sample.params[1].param_type is not ParameterTypes.std:
            raise TypeError("Second parameter must be std")
        if sample.params[1].param_val <= 0:
            raise ValueError("Standard deviation must be positive")

    elif sample.distribution_type == Distributions.weibull:
        if len(sample.params) != 2:
            raise TypeError("Weibull distribution requires exactly two "
                            + "parameters")
        if sample.params[0].param_type is not ParameterTypes.shape:
            raise TypeError("First parameter must be shape")
        if sample.params[1].param_type is not ParameterTypes.scale:
            raise TypeError("Second parameter must be scale")
        if sample.params[0].param_val <= 0:
            raise ValueError("Shape must be positive")
        if sample.params[1].param_val <= 0:
            raise ValueError("Scale must be positive")

    else:
        raise ValueError("Invalid distribution type")

    try:
        cursor = app.db_connection.cursor()
        try:
            cursor.execute("INSERT INTO sample_definitions (distribution_type,"
                           + " param_one, param_two, num_samples) VALUES "
                           + "(?, ?, ?, ?)",
                           (sample.distribution_type.value,
                            sample.params[0].param_val,
                            sample.params[1].param_val,
                            sample.num_samples))
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                cursor.execute("SELECT id FROM sample_definitions WHERE "
                               + "distribution_type = ? AND param_one = ? "
                               + "AND param_two = ? AND num_samples = ?",
                               (sample.distribution_type.value,
                                sample.params[0].param_val,
                                sample.params[1].param_val,
                                sample.num_samples))
                return {'ID': cursor.fetchone()[0]}
            else:
                app.db_connection.rollback()
                raise sqlite3.IntegrityError("Failed to insert sample into "
                                             + "database") from e
        ID = cursor.lastrowid
        app.db_connection.commit()
    except sqlite3.Error as e:
        app.db_connection.rollback()
        raise sqlite3.Error("Failed to insert sample into database.") from e
    finally:
        cursor.close()

    return {'ID': ID}


@app.get('/samples')
async def get_samples():
    """Get all samples in the database

    Returns
    -------
    List[Sample]
        A list of all samples in the database
    """

    try:
        cursor = app.db_connection.cursor()
        cursor.execute("SELECT * FROM sample_definitions")
        rows = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as e:
        raise sqlite3.Error("Failed to retrieve samples from database.") from e

    return rows


@app.get('/sample/{id}/statistics')
async def get_sample_statistics(id: int):
    """Get the statistics for a given sample identified by id

    Parameters
    ----------
    id : int
        The ID of the requested sample

    Returns
    -------
    Sample
        The sample with the given ID
    SampleStatistics
        The statistics for the sample
    """

    try:
        cursor = app.db_connection.cursor()
        cursor.execute("SELECT * FROM sample_definitions WHERE id = ?", (id,))
        sample_def = cursor.fetchone()
        cursor.close()
    except sqlite3.Error as e:
        raise sqlite3.Error("Failed to retrieve samples from database.") from e

    if sample_def is None:
        raise ValueError("No sample with ID {} exists".format(id))

    mean_dist = None
    std_dist = None

    rng = np.random.default_rng()

    if sample_def['distribution_type'] == Distributions.uniform.value:
        sample = rng.uniform(sample_def['param_one'],
                             sample_def['param_two'],
                             (sample_def['num_samples'], 1))
        mean_dist = (sample_def['param_one']
                     + sample_def['param_two']) / 2
        std_dist = (sample_def['param_two']
                    - sample_def['param_one']) / np.sqrt(12)

    elif sample_def['distribution_type'] == Distributions.normal.value:
        sample = rng.normal(sample_def['param_one'],
                            sample_def['param_two'],
                            (sample_def['num_samples'], 1))
        mean_dist = sample_def['param_one']
        std_dist = sample_def['param_two']

    elif sample_def['distribution_type'] == Distributions.weibull.value:
        sample = rng.weibull(sample_def['param_one'],
                             (sample_def['num_samples'], 1)) \
            * sample_def['param_two']
        mean_dist = sample_def['param_two'] \
            * gamma(1 + 1 / sample_def['param_one'])
        std_dist = sample_def['param_two'] \
            * np.sqrt(gamma(1 + 2 / sample_def['param_one'])
                      - np.square(gamma(1 + 1 / sample_def['param_one'])))

    else:
        raise ValueError("Distribution type not recognized")

    mean = np.mean(sample)
    std = np.std(sample, ddof=1)

    stats = SampleStatistics(
        mean_samples=mean,
        std_samples=std,
        mean_dist=mean_dist,
        std_dist=std_dist,
        error_mean=abs(mean - mean_dist),
        error_std=abs(std - std_dist)
    )

    return sample_def, stats

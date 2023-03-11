"""Main module for the FastAPI app

This module contains the FastAPI app and the endpoints for the API.

Functions
----------
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

from distributions import Distributions, ParameterTypes, Sample, SampleStatistics

ID = 1

db = {}

app = FastAPI()


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

    global ID

    if sample.distribution_type is Distributions.uniform:
        if len(sample.params) != 2:
            raise TypeError("Uniform distribution requires two parameters")
        if sample.params[0].param_type is not ParameterTypes.min:
            raise TypeError("First parameter must be min")
        if sample.params[1].param_type is not ParameterTypes.max:
            raise TypeError("Second parameter must be max")

    elif sample.distribution_type is Distributions.normal:
        if len(sample.params) != 2:
            raise TypeError("Normal distribution requires two parameters")
        if sample.params[0].param_type is not ParameterTypes.mean:
            raise TypeError("First parameter must be mean")
        if sample.params[1].param_type is not ParameterTypes.std:
            raise TypeError("Second parameter must be std")
        if sample.params[1].param_val <= 0:
            raise ValueError("Standard deviation must be positive")

    elif sample.distribution_type is Distributions.weibull:
        if len(sample.params) != 2:
            raise TypeError("Weibull distribution requires two parameters")
        if sample.params[0].param_type is not ParameterTypes.shape:
            raise TypeError("First parameter must be shape")
        if sample.params[1].param_type is not ParameterTypes.scale:
            raise TypeError("Second parameter must be scale")
        if sample.params[0].param_val <= 0:
            raise ValueError("Shape must be positive")
        if sample.params[1].param_val <= 0:
            raise ValueError("Scale must be positive")

    db[ID] = sample
    ID += 1
    return {"ID": ID-1}

#    return{"message": "Generate an new entry in the database for a sample"}
#    conn = sqlite3.connect('test.db')
#    c = conn.cursor()
#    c.execute("INSERT INTO test VALUES (?, ?)", (numpy.random.rand(), numpy.random.rand()))
#    conn.commit()
#    conn.close()
#    return {"message": "Hello World"}


@app.get('/samples')
async def get_samples():
    """Get all samples in the database
    
    Returns
    -------
    List[Sample]
        A list of all samples in the database
    """

    return db


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

    sample_def = db[id]

    mean_dist = None
    std_dist = None

    rng = np.random.default_rng()

    if sample_def.distribution_type is Distributions.uniform:
        sample = rng.uniform(sample_def.params[0].param_val,
                             sample_def.params[1].param_val,
                             (sample_def.num_samples, 1))
        mean_dist = (sample_def.params[0].param_val
                     + sample_def.params[1].param_val) / 2
        std_dist = (sample_def.params[1].param_val
                    - sample_def.params[0].param_val) / np.sqrt(12)

    elif sample_def.distribution_type is Distributions.normal:
        sample = rng.normal(sample_def.params[0].param_val,
                            sample_def.params[1].param_val,
                            (sample_def.num_samples, 1))
        mean_dist = sample_def.params[0].param_val
        std_dist = sample_def.params[1].param_val

    elif sample_def.distribution_type is Distributions.weibull:
        sample = rng.weibull(sample_def.params[0].param_val,
                             (sample_def.num_samples, 1)) \
                             * sample_def.params[1].param_val
        mean_dist = sample_def.params[1].param_val \
                    * gamma(1 + 1 / sample_def.params[0].param_val)
        std_dist = sample_def.params[1].param_val \
                    * np.sqrt(gamma(1 + 2 / sample_def.params[0].param_val)
                              - np.square(gamma(1 + 1 / sample_def.params[0].param_val)))

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

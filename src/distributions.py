"""Module for the distribution models

This module contains the models for the different types of distributions
and the different types of parameters. It also contains the models for
the sample and the sample statistics.

Classes
----------
    Distributions
        Enum for the different types of distributions
    ParameterTypes
        Enum for the different types of parameters
    Parameter
        Represent a single parameter for a distribution definition
    Sample
        Represent a single distribution sample
    SampleStatistics
        Represent the statistics for a single distribution sample
"""

from enum import Enum
from typing import List

from pydantic import BaseModel


class Distributions(Enum):
    """Enum for the different types of distributions

    Attributes
    ----------
    uniform : str
        Uniform distribution
    normal : str
        Normal distribution
    weibull : str
        Weibull distribution
    """

    uniform = 'uniform'
    normal = 'normal'
    weibull = 'weibull'


class ParameterTypes(Enum):
    """Enum for the different types of parameters

    Attributes
    ----------
    min : str
        Minimum value for e.g. a uniform distribution
    max : str
        Maximum value for e.g. a uniform distribution
    mean : str
        Mean value for e.g. a normal distribution
    std : str
        Standard deviation for e.g. a normal distribution
    shape : str
        Shape parameter for e.g. a weibull distribution
    scale : str
        Scale parameter for e.g. a weibull distribution
    """

    min = 'min'
    max = 'max'
    mean = 'mean'
    std = 'std'
    shape = 'shape'
    scale = 'scale'


class Parameter(BaseModel):
    """Represent a single parameter for a distribution definition

    Attributes
    ----------
    param_type : ParameterTypes
        The type of the parameter
    param_val : float
        The value of the parameter
    """

    param_type: ParameterTypes
    param_val: float


class Sample(BaseModel):
    """Represent a single distribution sample

    Attributes
    ----------
    distribution_type : Distributions
        The type of the distribution
    num_samples : int
        The number of samples to generate
    params : List[Parameter]
        A list of the parameters for the distribution
    """

    distribution_type: Distributions
    num_samples: int
    params: List[Parameter]


class SampleStatistics(BaseModel):
    """Represent the statistics for a single distribution sample

    Attributes
    ----------
    mean_samples : float
        The mean of the sample
    std_samples : float
        The standard deviation of the sample
    mean_dist : float
        The mean of the distribution
    std_dist : float
        The standard deviation of the distribution
    error_mean : float
        The absolute error in the mean of the sample
    error_std : float
        The absolute error in the standard deviation of the sample
    """

    mean_samples: float
    std_samples: float
    mean_dist: float
    std_dist: float
    error_mean: float
    error_std: float

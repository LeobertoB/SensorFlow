"""
Configuration settings for the sensor network simulation.
"""

from typing import Tuple
from pydantic import BaseModel, Field


class SensorConfig(BaseModel):
    """Configuration for individual sensors."""
    radius_range: Tuple[float, float] = Field(
        default=(5.0, 15.0),
        description="Range of possible sensor coverage radii (min, max)"
    )
    lifespan_range: Tuple[float, float] = Field(
        default=(30.0, 50.0),
        description="Range of possible sensor lifespans in time units (min, max)"
    )
    mobility_range: Tuple[float, float] = Field(
        default=(0.1, 1.0),
        description="Range of possible mobility factors (min, max)"
    )
    failure_probability_range: Tuple[float, float] = Field(
        default=(0.0, 0.05),
        description="Range of possible failure probabilities per time unit (min, max)"
    )


class NetworkConfig(BaseModel):
    """Configuration for the sensor network."""
    bounds: Tuple[float, float, float] = Field(
        default=(100.0, 100.0, 100.0),
        description="Size of the 3D space (x, y, z)"
    )
    initial_sensors: int = Field(
        default=20,
        description="Number of sensors to deploy initially"
    )
    coverage_threshold: float = Field(
        default=0.8,
        description="Minimum desired coverage ratio (0-1)"
    )
    healing_max_attempts: int = Field(
        default=5,
        description="Maximum number of healing attempts per time step"
    )


class SimulationConfig(BaseModel):
    """Main configuration for the simulation."""
    sensor: SensorConfig = Field(
        default_factory=SensorConfig,
        description="Configuration for sensors"
    )
    network: NetworkConfig = Field(
        default_factory=NetworkConfig,
        description="Configuration for the network"
    )
    simulation_steps: int = Field(
        default=10,
        description="Number of time steps to simulate"
    )
    save_history: bool = Field(
        default=True,
        description="Whether to save simulation history"
    )
    visualization_enabled: bool = Field(
        default=True,
        description="Whether to enable visualization"
    )
    random_seed: int = Field(
        default=None,
        description="Random seed for reproducibility"
    )

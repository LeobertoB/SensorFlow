"""
Base sensor implementations and sensor types.
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
from loguru import logger


@dataclass
class SensorStatus:
    """Status information for a sensor."""
    active: bool
    battery_level: float
    last_failure_check: float
    coverage_efficiency: float
    position_history: list


class BaseSensor:
    """Base class for all sensor types."""

    def __init__(
        self,
        id: int,
        position: np.ndarray,
        radius: float,
        lifespan: float,
        mobility_factor: float,
        failure_probability: float
    ):
        """
        Initialize a sensor.

        Args:
            id: Unique identifier for the sensor
            position: Initial 3D position (x, y, z)
            radius: Coverage radius
            lifespan: Initial lifespan
            mobility_factor: How much the sensor can move
            failure_probability: Probability of random failure per time unit
        """
        self.id = id
        self.position = position
        self.radius = radius
        self._initial_lifespan = lifespan
        self.lifespan = lifespan
        self.mobility_factor = mobility_factor
        self.failure_probability = failure_probability
        self.status = SensorStatus(
            active=True,
            battery_level=1.0,
            last_failure_check=0.0,
            coverage_efficiency=1.0,
            position_history=[position.copy()]
        )

    def degrade(self, time_step: float = 1.0) -> None:
        """
        Update sensor condition based on time passed.

        Args:
            time_step: Amount of time that has passed
        """
        if not self.status.active:
            return

        # Battery degradation
        battery_drain = time_step * (1.0 / self._initial_lifespan)
        self.status.battery_level = max(0.0, self.status.battery_level - battery_drain)
        
        if self.status.battery_level <= 0:
            self.status.active = False
            logger.info(f"Sensor {self.id} deactivated due to battery depletion")

    def move(self, bounds: Tuple[float, float, float]) -> None:
        """
        Update sensor position within bounds.

        Args:
            bounds: (x, y, z) dimensions of the space
        """
        if not self.status.active:
            return

        # Generate random displacement
        displacement = np.random.uniform(-1, 1, size=3) * self.mobility_factor
        
        # Ensure new position is within bounds
        new_position = self.position + displacement
        new_position = np.clip(new_position, [0, 0, 0], bounds)
        
        self.position = new_position
        self.status.position_history.append(new_position.copy())

    def check_failure(self) -> None:
        """Check for random failures."""
        if not self.status.active:
            return

        if np.random.random() < self.failure_probability:
            self.status.active = False
            logger.warning(f"Sensor {self.id} failed randomly")

    def covers(self, point: np.ndarray) -> bool:
        """
        Check if a point is within sensor's coverage.

        Args:
            point: 3D point to check

        Returns:
            bool: True if point is covered, False otherwise
        """
        if not self.status.active:
            return False
            
        return np.linalg.norm(self.position - point) <= self.radius

    def get_coverage_statistics(self) -> dict:
        """
        Get detailed coverage statistics.

        Returns:
            dict: Coverage statistics
        """
        return {
            'radius': self.radius,
            'coverage_volume': (4/3) * np.pi * (self.radius ** 3),
            'efficiency': self.status.coverage_efficiency,
            'active': self.status.active,
            'battery_level': self.status.battery_level
        }


class EconomySensor(BaseSensor):
    """Low-cost sensor with basic capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius *= 0.8  # Smaller coverage
        self.failure_probability *= 1.5  # Higher failure rate


class PremiumSensor(BaseSensor):
    """High-end sensor with enhanced capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius *= 1.2  # Larger coverage
        self.failure_probability *= 0.5  # Lower failure rate
        
    def move(self, bounds: Tuple[float, float, float]) -> None:
        """Enhanced movement with better stability."""
        super().move(bounds)
        # Add stabilization effect
        if len(self.status.position_history) >= 2:
            prev_pos = self.status.position_history[-2]
            self.position = 0.7 * self.position + 0.3 * prev_pos

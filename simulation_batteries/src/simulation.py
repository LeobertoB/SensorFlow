"""
Network simulation implementation.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger
from datetime import datetime
import json

from .models.sensors import BaseSensor, EconomySensor, PremiumSensor
from .config import SimulationConfig


class NetworkSimulation:
    """Main simulation class for sensor network."""

    def __init__(self, config: SimulationConfig):
        """
        Initialize the simulation.

        Args:
            config: Simulation configuration
        """
        self.config = config
        self.sensors: List[BaseSensor] = []
        self.sensor_counter = 0
        self.history: List[Dict[str, Any]] = []
        
        # Set random seed if specified
        if config.random_seed is not None:
            np.random.seed(config.random_seed)
            
        # Deploy initial sensors
        self._deploy_initial_sensors()
        
        logger.info(f"Initialized simulation with {len(self.sensors)} sensors")

    def _deploy_initial_sensors(self) -> None:
        """Deploy the initial set of sensors."""
        for _ in range(self.config.network.initial_sensors):
            # Randomly choose between sensor types
            if np.random.random() < 0.7:  # 70% economy sensors
                self._add_sensor(sensor_type=EconomySensor)
            else:  # 30% premium sensors
                self._add_sensor(sensor_type=PremiumSensor)

    def _add_sensor(self, sensor_type: type) -> None:
        """
        Add a new sensor to the network.

        Args:
            sensor_type: Type of sensor to add
        """
        config = self.config.sensor
        bounds = self.config.network.bounds
        
        # Generate random position
        position = np.array([
            np.random.uniform(0, bounds[0]),
            np.random.uniform(0, bounds[1]),
            np.random.uniform(0, bounds[2])
        ])
        
        # Create sensor with random parameters within configured ranges
        sensor = sensor_type(
            id=self.sensor_counter,
            position=position,
            radius=np.random.uniform(*config.radius_range),
            lifespan=np.random.uniform(*config.lifespan_range),
            mobility_factor=np.random.uniform(*config.mobility_range),
            failure_probability=np.random.uniform(*config.failure_probability_range)
        )
        
        self.sensors.append(sensor)
        self.sensor_counter += 1
        
        logger.debug(f"Added {sensor_type.__name__} sensor (ID: {sensor.id})")

    def run(self, steps: Optional[int] = None) -> None:
        """
        Run the simulation for a specified number of steps.

        Args:
            steps: Number of steps to simulate (uses config value if None)
        """
        steps = steps or self.config.simulation_steps
        
        for step in range(steps):
            logger.info(f"Starting simulation step {step + 1}/{steps}")
            
            # Update all sensors
            self._update_network()
            
            # Check and maintain coverage
            self._maintain_coverage()
            
            # Record state
            if self.config.save_history:
                self._record_state(step)
            
            # Log statistics
            self._log_statistics()

    def _update_network(self) -> None:
        """Update the state of all sensors."""
        for sensor in self.sensors:
            if sensor.status.active:
                sensor.move(self.config.network.bounds)
                sensor.check_failure()
                sensor.degrade()

    def _maintain_coverage(self) -> None:
        """Maintain network coverage by adding sensors if needed."""
        coverage = self.calculate_coverage()
        attempts = 0
        
        while (coverage < self.config.network.coverage_threshold and 
               attempts < self.config.network.healing_max_attempts):
            # Add a premium sensor for better healing
            self._add_sensor(PremiumSensor)
            coverage = self.calculate_coverage()
            attempts += 1
            
            logger.info(f"Added healing sensor. New coverage: {coverage:.2%}")

    def calculate_coverage(self, grid_density: int = 10) -> float:
        """
        Calculate the current coverage ratio.

        Args:
            grid_density: Number of points per dimension for sampling

        Returns:
            float: Coverage ratio (0-1)
        """
        bounds = self.config.network.bounds
        total_points = 0
        covered_points = 0
        
        # Create sampling grid
        x = np.linspace(0, bounds[0], grid_density)
        y = np.linspace(0, bounds[1], grid_density)
        z = np.linspace(0, bounds[2], grid_density)
        
        active_sensors = [s for s in self.sensors if s.status.active]
        
        if not active_sensors:
            return 0.0
        
        # Check coverage for each point
        for xi in x:
            for yi in y:
                for zi in z:
                    point = np.array([xi, yi, zi])
                    total_points += 1
                    if any(sensor.covers(point) for sensor in active_sensors):
                        covered_points += 1
        
        return covered_points / total_points if total_points > 0 else 0.0

    def _record_state(self, step: int) -> None:
        """
        Record the current state of the simulation.

        Args:
            step: Current simulation step
        """
        state = {
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'active_sensors': len([s for s in self.sensors if s.status.active]),
            'total_sensors': len(self.sensors),
            'coverage': self.calculate_coverage(),
            'sensors': [
                {
                    'id': sensor.id,
                    'type': sensor.__class__.__name__,
                    'position': sensor.position.tolist(),
                    'active': sensor.status.active,
                    'battery': sensor.status.battery_level,
                }
                for sensor in self.sensors
            ]
        }
        
        self.history.append(state)

    def _log_statistics(self) -> None:
        """Log current simulation statistics."""
        active_sensors = [s for s in self.sensors if s.status.active]
        coverage = self.calculate_coverage()
        
        logger.info(f"Network Statistics:")
        logger.info(f"- Active sensors: {len(active_sensors)}/{len(self.sensors)}")
        logger.info(f"- Coverage: {coverage:.2%}")
        logger.info(f"- Average battery level: {np.mean([s.status.battery_level for s in active_sensors]):.2%}")

    def save_history(self, filename: str) -> None:
        """
        Save simulation history to a file.

        Args:
            filename: Name of the file to save to
        """
        if not self.history:
            logger.warning("No history to save")
            return
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Saved simulation history to {filename}")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

"""
Unit tests for network simulation.
"""

import numpy as np
import pytest
from src.config import SimulationConfig
from src.simulation import NetworkSimulation


@pytest.fixture
def config():
    """Create a test configuration."""
    return SimulationConfig(
        simulation_steps=5,
        save_history=True,
        visualization_enabled=False,
        random_seed=42
    )


@pytest.fixture
def simulation(config):
    """Create a test simulation."""
    return NetworkSimulation(config)


def test_simulation_initialization(simulation):
    """Test simulation initialization."""
    assert len(simulation.sensors) == simulation.config.network.initial_sensors
    assert all(sensor.status.active for sensor in simulation.sensors)
    assert simulation.sensor_counter == len(simulation.sensors)


def test_coverage_calculation(simulation):
    """Test coverage calculation."""
    coverage = simulation.calculate_coverage(grid_density=5)
    assert 0 <= coverage <= 1


def test_network_update(simulation):
    """Test network update."""
    initial_positions = [sensor.position.copy() for sensor in simulation.sensors]
    initial_battery = [sensor.status.battery_level for sensor in simulation.sensors]
    
    simulation._update_network()
    
    # Check that sensors have moved
    current_positions = [sensor.position for sensor in simulation.sensors]
    assert not all(np.array_equal(pos1, pos2) for pos1, pos2 
                  in zip(initial_positions, current_positions))
    
    # Check that battery has degraded
    current_battery = [sensor.status.battery_level for sensor in simulation.sensors]
    assert all(b1 >= b2 for b1, b2 in zip(initial_battery, current_battery))


def test_coverage_maintenance(simulation):
    """Test coverage maintenance."""
    initial_sensors = len(simulation.sensors)
    
    # Force low coverage by deactivating most sensors
    for sensor in simulation.sensors[:-2]:  # Leave only 2 active
        sensor.status.active = False
    
    simulation._maintain_coverage()
    
    assert len(simulation.sensors) > initial_sensors


def test_history_recording(simulation):
    """Test history recording."""
    simulation.run(steps=2)
    
    assert len(simulation.history) == 2
    assert all(isinstance(state, dict) for state in simulation.history)
    assert all('step' in state for state in simulation.history)
    assert all('coverage' in state for state in simulation.history)


def test_sensor_types_distribution(simulation):
    """Test distribution of sensor types."""
    economy_count = sum(1 for s in simulation.sensors if s.__class__.__name__ == 'EconomySensor')
    premium_count = sum(1 for s in simulation.sensors if s.__class__.__name__ == 'PremiumSensor')
    
    assert economy_count + premium_count == len(simulation.sensors)
    # Roughly 70-30 distribution (allowing for random variation)
    assert 0.5 <= economy_count / len(simulation.sensors) <= 0.9

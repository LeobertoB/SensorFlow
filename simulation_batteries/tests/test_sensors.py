"""
Unit tests for sensor models.
"""

import numpy as np
import pytest
from src.models.sensors import BaseSensor, EconomySensor, PremiumSensor


@pytest.fixture
def base_sensor():
    """Create a basic sensor for testing."""
    return BaseSensor(
        id=1,
        position=np.array([0.0, 0.0, 0.0]),
        radius=10.0,
        lifespan=100.0,
        mobility_factor=0.5,
        failure_probability=0.01
    )


def test_sensor_initialization(base_sensor):
    """Test sensor initialization."""
    assert base_sensor.id == 1
    assert np.array_equal(base_sensor.position, np.array([0.0, 0.0, 0.0]))
    assert base_sensor.radius == 10.0
    assert base_sensor.status.active
    assert base_sensor.status.battery_level == 1.0


def test_sensor_coverage(base_sensor):
    """Test sensor coverage detection."""
    # Point within radius
    assert base_sensor.covers(np.array([5.0, 5.0, 5.0]))
    
    # Point outside radius
    assert not base_sensor.covers(np.array([20.0, 20.0, 20.0]))


def test_sensor_degrade(base_sensor):
    """Test sensor degradation."""
    initial_battery = base_sensor.status.battery_level
    base_sensor.degrade(time_step=10.0)
    assert base_sensor.status.battery_level < initial_battery
    assert base_sensor.status.active


def test_sensor_complete_depletion(base_sensor):
    """Test sensor deactivation on complete battery depletion."""
    base_sensor.degrade(time_step=1000.0)  # Large time step
    assert not base_sensor.status.active
    assert base_sensor.status.battery_level == 0.0


def test_sensor_movement(base_sensor):
    """Test sensor movement."""
    initial_position = base_sensor.position.copy()
    bounds = (100.0, 100.0, 100.0)
    
    base_sensor.move(bounds)
    
    assert not np.array_equal(base_sensor.position, initial_position)
    assert all(0 <= coord <= bound for coord, bound in zip(base_sensor.position, bounds))


def test_economy_sensor():
    """Test economy sensor specific features."""
    sensor = EconomySensor(
        id=2,
        position=np.array([0.0, 0.0, 0.0]),
        radius=10.0,
        lifespan=100.0,
        mobility_factor=0.5,
        failure_probability=0.01
    )
    
    assert sensor.radius == 8.0  # 80% of base radius
    assert sensor.failure_probability == 0.015  # 150% of base probability


def test_premium_sensor():
    """Test premium sensor specific features."""
    sensor = PremiumSensor(
        id=3,
        position=np.array([0.0, 0.0, 0.0]),
        radius=10.0,
        lifespan=100.0,
        mobility_factor=0.5,
        failure_probability=0.01
    )
    
    assert sensor.radius == 12.0  # 120% of base radius
    assert sensor.failure_probability == 0.005  # 50% of base probability
    
    # Test movement stabilization
    initial_position = sensor.position.copy()
    bounds = (100.0, 100.0, 100.0)
    
    sensor.move(bounds)
    first_move = sensor.position.copy()
    
    sensor.move(bounds)
    second_move = sensor.position.copy()
    
    # Verify that second movement was influenced by previous position
    assert np.any(np.abs(second_move - first_move) <= np.abs(first_move - initial_position))

"""
Example usage of the sensor network simulation.
"""

from src.config import SimulationConfig
from src.simulation import NetworkSimulation
from src.visualization.visualizer import NetworkVisualizer

def main():
    # Create configuration
    config = SimulationConfig(
        simulation_steps=20,
        save_history=True,
        visualization_enabled=True
    )
    
    # Initialize and run simulation
    simulation = NetworkSimulation(config)
    simulation.run()
    
    # Visualize results
    if config.visualization_enabled:
        # Plot 2D coverage
        NetworkVisualizer.plot_2d_coverage(
            simulation.sensors,
            config.network.bounds,
            plane="xy"
        )
        
        # Plot 3D network
        NetworkVisualizer.plot_3d_network(
            simulation.sensors,
            config.network.bounds,
            show_coverage=True
        )
        
        # Plot statistics
        NetworkVisualizer.plot_network_statistics(simulation.history)
    
    # Save simulation history
    simulation.save_history("simulation_results.json")

if __name__ == "__main__":
    main()

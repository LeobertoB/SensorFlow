"""
Advanced POC demonstrating a complex sensor network scenario.
"""

from src.config import SimulationConfig
from src.simulation import NetworkSimulation
from src.visualization.visualizer import NetworkVisualizer
import numpy as np
import matplotlib.pyplot as plt
import json


def run_coverage_analysis():
    """Run multiple simulations with different parameters and analyze results."""
    # Test different initial sensor counts
    sensor_counts = [10, 20, 30, 40, 50]
    coverage_results = []
    
    for count in sensor_counts:
        config = SimulationConfig(
            simulation_steps=30,
            save_history=True,
            visualization_enabled=False
        )
        config.network.initial_sensors = count
        
        simulation = NetworkSimulation(config)
        simulation.run()
        
        # Calculate average coverage over time
        avg_coverage = np.mean([state['coverage'] for state in simulation.history])
        coverage_results.append(avg_coverage)
        
        # Save results
        with open(f'results_sensors_{count}.json', 'w') as f:
            json.dump(simulation.history, f, indent=2)
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(sensor_counts, coverage_results, 'bo-')
    plt.xlabel('Number of Initial Sensors')
    plt.ylabel('Average Coverage Ratio')
    plt.title('Coverage Analysis')
    plt.grid(True)
    plt.savefig('coverage_analysis.png')
    plt.close()


def run_failure_analysis():
    """Analyze the impact of different failure probabilities."""
    failure_probs = [0.01, 0.05, 0.1, 0.15, 0.2]
    survival_rates = []
    
    for prob in failure_probs:
        config = SimulationConfig(
            simulation_steps=50,
            save_history=True,
            visualization_enabled=False
        )
        config.sensor.failure_probability_range = (prob, prob)
        
        simulation = NetworkSimulation(config)
        simulation.run()
        
        # Calculate survival rate
        final_state = simulation.history[-1]
        survival_rate = final_state['active_sensors'] / final_state['total_sensors']
        survival_rates.append(survival_rate)
        
        # Save results
        with open(f'results_failure_{prob:.2f}.json', 'w') as f:
            json.dump(simulation.history, f, indent=2)
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(failure_probs, survival_rates, 'ro-')
    plt.xlabel('Failure Probability')
    plt.ylabel('Survival Rate')
    plt.title('Failure Analysis')
    plt.grid(True)
    plt.savefig('failure_analysis.png')
    plt.close()


def run_cost_benefit_analysis():
    """Analyze the cost-benefit ratio of different sensor type distributions."""
    premium_ratios = [0.0, 0.25, 0.5, 0.75, 1.0]
    cost_benefit_results = []
    
    base_cost = {
        'EconomySensor': 1.0,
        'PremiumSensor': 2.5
    }
    
    for premium_ratio in premium_ratios:
        config = SimulationConfig(
            simulation_steps=40,
            save_history=True,
            visualization_enabled=False
        )
        
        simulation = NetworkSimulation(config)
        
        # Override sensor deployment to control ratio
        total_sensors = config.network.initial_sensors
        premium_count = int(total_sensors * premium_ratio)
        economy_count = total_sensors - premium_count
        
        # Calculate costs
        total_cost = (economy_count * base_cost['EconomySensor'] + 
                     premium_count * base_cost['PremiumSensor'])
        
        simulation.run()
        
        # Calculate benefit (average coverage / cost)
        avg_coverage = np.mean([state['coverage'] for state in simulation.history])
        cost_benefit = avg_coverage / total_cost
        cost_benefit_results.append(cost_benefit)
        
        # Save results
        with open(f'results_premium_ratio_{premium_ratio:.2f}.json', 'w') as f:
            json.dump(simulation.history, f, indent=2)
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(premium_ratios, cost_benefit_results, 'go-')
    plt.xlabel('Premium Sensor Ratio')
    plt.ylabel('Cost-Benefit Ratio')
    plt.title('Cost-Benefit Analysis')
    plt.grid(True)
    plt.savefig('cost_benefit_analysis.png')
    plt.close()


def main():
    """Run all analyses."""
    print("Running coverage analysis...")
    run_coverage_analysis()
    
    print("Running failure analysis...")
    run_failure_analysis()
    
    print("Running cost-benefit analysis...")
    run_cost_benefit_analysis()
    
    print("Analyses complete. Check the generated JSON files and plots for results.")


if __name__ == "__main__":
    main()

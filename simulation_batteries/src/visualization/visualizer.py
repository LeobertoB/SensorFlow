"""
Visualization tools for sensor network simulation.
"""

from typing import List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ..models.sensors import BaseSensor, PremiumSensor


class NetworkVisualizer:
    """Visualization tools for sensor networks."""

    @staticmethod
    def plot_2d_coverage(
        sensors: List[BaseSensor],
        bounds: Tuple[float, float, float],
        plane: str = "xy"
    ) -> None:
        """
        Plot 2D coverage on a specified plane.

        Args:
            sensors: List of sensors to visualize
            bounds: Space boundaries (x, y, z)
            plane: Plane to visualize ('xy', 'xz', or 'yz')
        """
        active_sensors = [s for s in sensors if s.status.active]
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw coverage circles for each sensor
        for sensor in active_sensors:
            if plane == "xy":
                center = (sensor.position[0], sensor.position[1])
                color = 'blue'
            elif plane == "xz":
                center = (sensor.position[0], sensor.position[2])
                color = 'green'
            else:  # yz
                center = (sensor.position[1], sensor.position[2])
                color = 'red'
                
            circle = plt.Circle(
                center,
                sensor.radius,
                color=color,
                alpha=0.3
            )
            ax.add_artist(circle)
        
        # Set plot limits and labels
        ax.set_xlim(0, bounds[0] if plane[0] == 'x' else bounds[1])
        ax.set_ylim(0, bounds[1] if plane[1] == 'y' else bounds[2])
        ax.set_aspect('equal')
        
        plt.title(f"Coverage on {plane.upper()} Plane")
        plt.xlabel(plane[0].upper())
        plt.ylabel(plane[1].upper())
        plt.grid(True)
        plt.show()

    @staticmethod
    def plot_3d_network(
        sensors: List[BaseSensor],
        bounds: Tuple[float, float, float],
        show_coverage: bool = True
    ) -> None:
        """
        Create an interactive 3D visualization of the network.

        Args:
            sensors: List of sensors to visualize
            bounds: Space boundaries (x, y, z)
            show_coverage: Whether to show coverage spheres
        """
        active_sensors = [s for s in sensors if s.status.active]
        
        # Create figure
        fig = go.Figure()
        
        # Add sensors
        for sensor in active_sensors:
            # Add sensor point
            fig.add_trace(go.Scatter3d(
                x=[sensor.position[0]],
                y=[sensor.position[1]],
                z=[sensor.position[2]],
                mode='markers',
                marker=dict(
                    size=8,
                    color='red' if isinstance(sensor, 'PremiumSensor') else 'blue',
                ),
                name=f'Sensor {sensor.id}'
            ))
            
            if show_coverage:
                # Create sphere surface points
                phi = np.linspace(0, 2*np.pi, 20)
                theta = np.linspace(-np.pi/2, np.pi/2, 20)
                phi, theta = np.meshgrid(phi, theta)
                
                x = sensor.position[0] + sensor.radius * np.cos(theta) * np.cos(phi)
                y = sensor.position[1] + sensor.radius * np.cos(theta) * np.sin(phi)
                z = sensor.position[2] + sensor.radius * np.sin(theta)
                
                # Add coverage sphere
                fig.add_trace(go.Surface(
                    x=x, y=y, z=z,
                    opacity=0.2,
                    showscale=False,
                    name=f'Coverage {sensor.id}'
                ))
        
        # Update layout
        fig.update_layout(
            title='3D Sensor Network',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='cube',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True
        )
        
        fig.show()

    @staticmethod
    def plot_network_statistics(history: List[dict]) -> None:
        """
        Plot network statistics over time.

        Args:
            history: List of recorded simulation states
        """
        if not history:
            return
            
        steps = [state['step'] for state in history]
        coverage = [state['coverage'] for state in history]
        active_sensors = [state['active_sensors'] for state in history]
        total_sensors = [state['total_sensors'] for state in history]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Network Coverage', 'Sensor Count')
        )
        
        # Add coverage trace
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=coverage,
                name='Coverage Ratio',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # Add sensor count traces
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=active_sensors,
                name='Active Sensors',
                line=dict(color='green')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=total_sensors,
                name='Total Sensors',
                line=dict(color='red')
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text='Network Statistics Over Time',
            showlegend=True
        )
        
        # Update y-axes labels
        fig.update_yaxes(title_text='Coverage Ratio', row=1, col=1)
        fig.update_yaxes(title_text='Number of Sensors', row=2, col=1)
        
        fig.show()

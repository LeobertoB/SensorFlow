# %%
import random
import numpy as np
import matplotlib.pyplot as plt


class Sensor:
    """
    Rappresenta un singolo sensore nello spazio 3D, con posizione, raggio di copertura e vita utile.
    """

    def __init__(self, id, x, y, z, radius, lifespan):
        self.id = id
        self.position = np.array([x, y, z], dtype=float)
        self.radius = radius
        self.lifespan = lifespan
        self.active = True

    def degrade(self):
        """
        Riduce la vita utile del sensore; lo disattiva se scende a zero.
        """
        self.lifespan -= random.uniform(0.5, 2.0)
        if self.lifespan <= 0:
            self.active = False

    def move(self, movement_range=0.5):
        """
        Sposta leggermente il sensore in modo casuale, se ancora attivo.
        """
        if not self.active:
            return
        displacement = np.random.uniform(-movement_range, movement_range, size=3)
        self.position += displacement

    def covers(self, point):
        """
        Verifica se un punto specifico rientra nel raggio di copertura del sensore.
        """
        return np.linalg.norm(self.position - point) <= self.radius


class SensorNetwork:
    """
    Gestisce una rete di sensori 3D, simulandone l'evoluzione e la copertura dinamica.
    """

    def __init__(self, num_sensors, bounds, radius_range, lifespan_range):
        self.sensors = []
        self.bounds = bounds
        self.radius_range = radius_range
        self.lifespan_range = lifespan_range
        self.sensor_counter = 0
        self.deploy_initial_sensors(num_sensors)

    def deploy_initial_sensors(self, num):
        """
        Crea i sensori iniziali posizionandoli randomicamente.
        """
        for _ in range(num):
            self.add_sensor()

    def add_sensor(self):
        """
        Aggiunge un nuovo sensore con parametri casuali.
        """
        x, y, z = [random.uniform(0, b) for b in self.bounds]
        radius = random.uniform(*self.radius_range)
        lifespan = random.uniform(*self.lifespan_range)
        sensor = Sensor(self.sensor_counter, x, y, z, radius, lifespan)
        self.sensors.append(sensor)
        self.sensor_counter += 1

    def update(self):
        """
        Aggiorna movimento e stato di ciascun sensore.
        """
        for sensor in self.sensors:
            sensor.move()
            sensor.degrade()

    def active_sensors(self):
        """
        Restituisce la lista dei sensori attualmente attivi.
        """
        return [s for s in self.sensors if s.active]

    def coverage_ratio(self, grid_density=10):
        """
        Calcola la percentuale dello spazio coperta dai sensori attivi.
        """
        total_points = 0
        covered_points = 0
        x = np.linspace(0, self.bounds[0], grid_density)
        y = np.linspace(0, self.bounds[1], grid_density)
        z = np.linspace(0, self.bounds[2], grid_density)

        active = self.active_sensors()
        if not active:
            return 0

        for xi in x:
            for yi in y:
                for zi in z:
                    point = np.array([xi, yi, zi])
                    total_points += 1
                    if any(sensor.covers(point) for sensor in active):
                        covered_points += 1

        return covered_points / total_points if total_points > 0 else 0

    def heal_network(self, coverage_threshold=0.8, max_attempts=5):
        """
        Migliora la rete aggiungendo sensori finché la copertura supera la soglia o si raggiunge il massimo numero di tentativi.
        """
        current_coverage = self.coverage_ratio(grid_density=10)
        attempts = 0
        while current_coverage < coverage_threshold and attempts < max_attempts:
            self.add_sensor()
            current_coverage = self.coverage_ratio(grid_density=10)
            attempts += 1

    def plot_coverage(self, plane="xy"):
        """
        Visualizza la copertura proiettata su un piano specificato (xy, xz, yz).
        """
        active = self.active_sensors()
        fig, ax = plt.subplots()
        for sensor in active:
            if plane == "xy":
                circle = plt.Circle(
                    (sensor.position[0], sensor.position[1]),
                    sensor.radius,
                    color="blue",
                    alpha=0.3,
                )
                ax.add_artist(circle)
            elif plane == "xz":
                circle = plt.Circle(
                    (sensor.position[0], sensor.position[2]),
                    sensor.radius,
                    color="green",
                    alpha=0.3,
                )
                ax.add_artist(circle)
            elif plane == "yz":
                circle = plt.Circle(
                    (sensor.position[1], sensor.position[2]),
                    sensor.radius,
                    color="red",
                    alpha=0.3,
                )
                ax.add_artist(circle)
        ax.set_xlim(0, self.bounds[0])
        ax.set_ylim(0, self.bounds[1] if plane == "xy" else self.bounds[2])
        ax.set_aspect("equal")
        plt.title(f"Copertura Piano {plane.upper()}")
        plt.xlabel(plane[0].upper())
        plt.ylabel(plane[1].upper())
        plt.show()


def simulate_network(steps=10, coverage_threshold=0.8):
    """
    Simula l'evoluzione della rete di sensori per un certo numero di passi temporali.
    """
    bounds = (100, 100, 100)
    radius_range = (5, 15)
    lifespan_range = (30, 50)
    network = SensorNetwork(
        num_sensors=20,
        bounds=bounds,
        radius_range=radius_range,
        lifespan_range=lifespan_range,
    )

    for step in range(steps):
        print(f"Simulazione passo {step+1}")
        network.update()
        network.heal_network(coverage_threshold=coverage_threshold, max_attempts=5)
        for plane in ["xy", "xz", "yz"]:
            network.plot_coverage(plane=plane)


if __name__ == "__main__":
    simulate_network(steps=5)

# %%

## METODO SECONDO ##

import random
import numpy as np
import matplotlib.pyplot as plt


class Sensor:
    """
    Rappresenta un sensore 3D con posizione, raggio, vita utile, fattore di mobilità e probabilità di guasto.
    """

    def __init__(
        self, id, x, y, z, radius, lifespan, mobility_factor, failure_probability
    ):
        self.id = id
        self.position = np.array([x, y, z], dtype=float)
        self.radius = radius
        self.lifespan = lifespan
        self.mobility_factor = mobility_factor
        self.failure_probability = failure_probability
        self.active = True

    def degrade(self):
        """
        Riduce progressivamente la vita utile del sensore.
        """
        self.lifespan -= random.uniform(0.5, 2.0)
        if self.lifespan <= 0:
            self.active = False

    def move(self):
        """
        Sposta il sensore in modo casuale, influenzato dal fattore di mobilità.
        """
        if not self.active:
            return
        displacement = np.random.uniform(-1, 1, size=3) * self.mobility_factor
        self.position += displacement

    def check_failure(self):
        """
        Verifica se il sensore subisce un guasto improvviso.
        """
        if not self.active:
            return
        if random.random() < self.failure_probability:
            self.active = False

    def covers(self, point):
        """
        Determina se un punto è coperto dal sensore.
        """
        return np.linalg.norm(self.position - point) <= self.radius


class SensorNetwork:
    """
    Gestisce una rete dinamica di sensori nello spazio tridimensionale.
    """

    def __init__(
        self,
        num_sensors,
        bounds,
        radius_range,
        lifespan_range,
        mobility_range,
        failure_probability_range,
    ):
        self.sensors = []
        self.bounds = bounds
        self.radius_range = radius_range
        self.lifespan_range = lifespan_range
        self.mobility_range = mobility_range
        self.failure_probability_range = failure_probability_range
        self.sensor_counter = 0
        self.deploy_initial_sensors(num_sensors)

    def deploy_initial_sensors(self, num):
        """
        Crea i sensori iniziali con parametri randomizzati.
        """
        for _ in range(num):
            self.add_sensor()

    def add_sensor(self):
        """
        Aggiunge un nuovo sensore alla rete.
        """
        x, y, z = [random.uniform(0, b) for b in self.bounds]
        radius = random.uniform(*self.radius_range)
        lifespan = random.uniform(*self.lifespan_range)
        mobility = random.uniform(*self.mobility_range)
        failure_prob = random.uniform(*self.failure_probability_range)
        sensor = Sensor(
            self.sensor_counter, x, y, z, radius, lifespan, mobility, failure_prob
        )
        self.sensors.append(sensor)
        self.sensor_counter += 1

    def update(self):
        """
        Aggiorna lo stato di ogni sensore: movimento, guasto e degradazione.
        """
        for sensor in self.sensors:
            sensor.move()
            sensor.check_failure()
            sensor.degrade()

    def active_sensors(self):
        """
        Restituisce l'elenco dei sensori attivi.
        """
        return [s for s in self.sensors if s.active]

    def coverage_ratio(self, grid_density=10):
        """
        Stima la copertura della rete su una griglia tridimensionale.
        """
        total_points = 0
        covered_points = 0
        x = np.linspace(0, self.bounds[0], grid_density)
        y = np.linspace(0, self.bounds[1], grid_density)
        z = np.linspace(0, self.bounds[2], grid_density)

        active = self.active_sensors()
        if not active:
            return 0

        for xi in x:
            for yi in y:
                for zi in z:
                    point = np.array([xi, yi, zi])
                    total_points += 1
                    if any(sensor.covers(point) for sensor in active):
                        covered_points += 1

        return covered_points / total_points if total_points > 0 else 0

    def heal_network(self, coverage_threshold=0.8, max_attempts=5):
        """
        Ristabilisce la copertura aggiungendo sensori finché necessario.
        """
        current_coverage = self.coverage_ratio(grid_density=10)
        attempts = 0
        while current_coverage < coverage_threshold and attempts < max_attempts:
            self.add_sensor()
            current_coverage = self.coverage_ratio(grid_density=10)
            attempts += 1

    def plot_coverage(self, plane="xy"):
        """
        Visualizza la copertura della rete su un piano specifico.
        """
        active = self.active_sensors()
        fig, ax = plt.subplots()
        for sensor in active:
            if plane == "xy":
                circle = plt.Circle(
                    (sensor.position[0], sensor.position[1]),
                    sensor.radius,
                    color="blue",
                    alpha=0.3,
                )
                ax.add_artist(circle)
            elif plane == "xz":
                circle = plt.Circle(
                    (sensor.position[0], sensor.position[2]),
                    sensor.radius,
                    color="green",
                    alpha=0.3,
                )
                ax.add_artist(circle)
            elif plane == "yz":
                circle = plt.Circle(
                    (sensor.position[1], sensor.position[2]),
                    sensor.radius,
                    color="red",
                    alpha=0.3,
                )
                ax.add_artist(circle)
        ax.set_xlim(0, self.bounds[0])
        ax.set_ylim(0, self.bounds[1] if plane == "xy" else self.bounds[2])
        ax.set_aspect("equal")
        plt.title(f"Copertura Piano {plane.upper()}")
        plt.xlabel(plane[0].upper())
        plt.ylabel(plane[1].upper())
        plt.show()


def simulate_network(steps=10, coverage_threshold=0.8):
    """
    Simula l'evoluzione della rete nel tempo.
    """
    bounds = (100, 100, 100)
    radius_range = (5, 15)
    lifespan_range = (30, 50)
    mobility_range = (0.1, 1.0)
    failure_probability_range = (0.0, 0.05)

    network = SensorNetwork(
        num_sensors=20,
        bounds=bounds,
        radius_range=radius_range,
        lifespan_range=lifespan_range,
        mobility_range=mobility_range,
        failure_probability_range=failure_probability_range,
    )

    for step in range(steps):
        print(f"Simulazione passo {step+1}")
        network.update()
        network.heal_network(coverage_threshold=coverage_threshold, max_attempts=5)
        for plane in ["xy", "xz", "yz"]:
            network.plot_coverage(plane=plane)


if __name__ == "__main__":
    simulate_network(steps=5)

# %%

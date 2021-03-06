import math
import numpy as np
from model.quadcopter import Quadcopter

class Environment(object):
    """
    Very simple environment. The quadcopter starts at position (0, 0, 3).

    The goal is to reach setpoint z=5 in 2 seconds (so, they need to "go up"),
    then to reach setpoint z=3 in other 2 seconds (so, "go down").

    Fitness is computed as to cumulative distance from the setpoint at each
    step
    """

    def __init__(self, z0, z1, total_t=2, dt=0.01, show=False):
        self.total_t = total_t
        self.z0 = z0
        self.z1 = z1
        self.dt = dt
        self.show = show
        self.prev_distance = float('-inf')
        self.plotter = None
        if self.show:
            from plotter.quadplotter import QuadPlotter, RED, GREEN
            self.plotter = QuadPlotter()
            self.plotter.add_marker((0, 0, z1), RED)

    def run(self, creature):
        quad = Quadcopter()
        quad.position = (0, 0, self.z0)
        z_setpoint = self.z1 # first task: go to setpoint (0, 0, z1)
        fitness = 0
        while quad.t < self.total_t:
            ## if quad.t >= 2:
            ##     # switch to second task
            ##     z_setpoint = self.z2
            #
            inputs = [z_setpoint, quad.position.z]
            outputs = creature.run_step(inputs)
            assert len(outputs) == 1
            pwm = outputs[0]
            quad.set_thrust(pwm, pwm, pwm, pwm)
            quad.step(self.dt)
            fitness += self.compute_fitness(quad, z_setpoint)
            self.show_step(quad)
        return fitness

    def show_step(self, quad):
        if self.show:
            self.plotter.update(quad)
            self.plotter.show_step()

    def compute_fitness(self, quad, z_setpoint):
        # for now, the goal is to reach the target position as fast as
        # possible and then to stay there. So a measure of the fitness is the
        # distance to the target at every step (the goal is to *minimize* the
        # total value, of course)
        x0, y0, z0 = 0, 0, z_setpoint
        x1, y1, z1 = quad.position
        distance = math.sqrt((x0-x1)**2 + (y0-y1)**2 + (z0-z1)**2)
        k = 1
        if distance > self.prev_distance:
            k = 3 # if we are overshooting, pay a penalty
        self.prev_distance = distance
        return distance * k

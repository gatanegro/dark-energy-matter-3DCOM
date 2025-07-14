import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D

# --- Constants ---
LZ = 1.23498228
HQS = 0.235
alpha = 0.0072973525693
x_param = 16.45
a0 = 5.29e-11  # Bohr radius in meters

# --- Bridge Formula ---
def bridge_formula(n):
    return a0 * (LZ**(np.pi * n)) * ((HQS / alpha)**(1 / x_param))

# --- Octave Reduction and Mapping ---
def reduce_to_single_digit(value):
    return (value - 1) % 9 + 1

def map_to_octave(value, layer):
    angle = (value / 9) * 2 * np.pi
    x = np.cos(angle) * (layer + 1)
    y = np.sin(angle) * (layer + 1)
    return x, y, angle

# --- Collatz Sequence Generation ---
def generate_collatz_sequence(n):
    sequence = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        sequence.append(n)
    return sequence

# --- Data Preparation ---
collatz_data = {n: generate_collatz_sequence(n) for n in range(1, 21)}
stack_spacing = 1.0
nodes = []

# Collect nodes from sequences
for number, sequence in collatz_data.items():
    for layer, value in enumerate(sequence):
        reduced = reduce_to_single_digit(value)
        x, y, theta = map_to_octave(reduced, layer)
        z = layer * stack_spacing
        nodes.append((x, y, z, theta, layer))

# --- Plot Setup ---
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.25)

# Initial observer angle (in degrees)
initial_theta_obs = 0

# Initial scatter plot (all gray)
sc = ax.scatter(*zip(*[(x, y, z) for x, y, z, t, l in nodes]), c='gray', s=20)

# Slider for observer angle
ax_angle = plt.axes([0.25, 0.12, 0.5, 0.03])
slider_angle = Slider(ax_angle, 'Observer Angle (°)', 0, 360, valinit=initial_theta_obs)

# Text box for bridge formula outputs
bridge_text = plt.figtext(0.15, 0.02, "", fontsize=10)

# Angular visibility threshold for observer to "see" a node
angle_threshold = np.pi / 12  # ~15 degrees

# --- Update Function ---
def update(val):
    theta_obs = np.radians(slider_angle.val)
    visible_nodes = []
    colors = []
    output_text = ""

    for x, y, z, theta, layer in nodes:
        # Check angular difference
        diff = abs(theta - theta_obs)
        diff = min(diff, 2 * np.pi - diff)

        if diff < angle_threshold:
            visible_nodes.append((x, y, z))
            colors.append('red')
            output_text += f"Layer {layer}: R = {bridge_formula(layer):.2e} m\n"
        else:
            visible_nodes.append((x, y, z))
            colors.append('gray')

    sc._offsets3d = tuple(zip(*visible_nodes))
    sc.set_color(colors)
    bridge_text.set_text(output_text)
    fig.canvas.draw_idle()

slider_angle.on_changed(update)

# --- Axis Settings ---
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_zlim(0, 20)
ax.set_xlabel("X (Octave Phase)")
ax.set_ylabel("Y (Octave Phase)")
ax.set_zlabel("Z (Recursion Depth)")
ax.set_title("3DCOM Observer-Angle Simulation with Bridge Formula Overlay")

# Initial render
update(initial_theta_obs)

# --- Show the plot ---
plt.show()

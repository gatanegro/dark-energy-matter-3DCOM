import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d import Axes3D
import csv

# --- Constants ---
LZ = 1.23498228
HQS = 0.235
alpha = 0.0072973525693
x_param = 16.45
a0 = 5.29e-11  # Bohr radius in meters

# --- Bridge Formula ---
def bridge_formula(n):
    return a0 * (LZ**(np.pi * n)) * ((HQS / alpha)**(1 / x_param))

# --- Octave Mapping ---
def reduce_to_single_digit(value):
    return (value - 1) % 9 + 1

def map_to_octave(value, layer):
    angle = (value / 9) * 2 * np.pi
    x = np.cos(angle) * (layer + 1)
    y = np.sin(angle) * (layer + 1)
    return x, y, angle

# --- Collatz Generator ---
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

for number, sequence in collatz_data.items():
    for layer, value in enumerate(sequence):
        reduced = reduce_to_single_digit(value)
        x, y, theta = map_to_octave(reduced, layer)
        z = layer * stack_spacing
        nodes.append((x, y, z, theta, layer, number, value))

# --- GUI Setup ---
fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.3)

initial_theta_obs = 0
angle_threshold = np.pi / 12  # Visibility threshold

sc = ax.scatter(*zip(*[(x, y, z) for x, y, z, *_ in nodes]), c='gray', s=20)

# Slider for observer angle
ax_angle = plt.axes([0.25, 0.18, 0.5, 0.03])
slider_angle = Slider(ax_angle, 'Observer Angle (°)', 0, 360, valinit=initial_theta_obs)

# Text field for outputs
bridge_text = plt.figtext(0.15, 0.04, "", fontsize=10, wrap=True)

# Button to save visible data
ax_button = plt.axes([0.8, 0.025, 0.15, 0.05])
button_save = Button(ax_button, 'Save Visible Nodes')

# --- Update Function ---
def update(val):
    theta_obs = np.radians(slider_angle.val)
    visible_nodes = []
    colors = []
    output_text = ""

    global last_visible_export
    last_visible_export = []

    for x, y, z, theta, layer, seed, value in nodes:
        diff = abs(theta - theta_obs)
        diff = min(diff, 2 * np.pi - diff)

        if diff < angle_threshold:
            visible_nodes.append((x, y, z))
            colors.append('red')
            R = bridge_formula(layer)
            output_text += f"n={layer}, seed={seed}, val={value} → R={R:.2e} m\n"
            last_visible_export.append((layer, seed, value, R))
        else:
            visible_nodes.append((x, y, z))
            colors.append('gray')

    sc._offsets3d = tuple(zip(*visible_nodes))
    sc.set_color(colors)
    bridge_text.set_text(output_text)
    fig.canvas.draw_idle()

# --- Save Function ---
def save_visible_nodes(event):
    with open("visible_nodes.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Layer", "Seed", "Value", "Bridge_Radius_m"])
        for row in last_visible_export:
            writer.writerow(row)
    print("Visible nodes saved to 'visible_nodes.csv'")

slider_angle.on_changed(update)
button_save.on_clicked(save_visible_nodes)

# --- Axes and Titles ---
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_zlim(0, 20)
ax.set_xlabel("X (Octave Phase)")
ax.set_ylabel("Y (Octave Phase)")
ax.set_zlabel("Z (Recursion Depth)")
ax.set_title("3DCOM Observer-Angle Simulator with Bridge Formula")

# Initial render
last_visible_export = []
update(initial_theta_obs)
plt.show()
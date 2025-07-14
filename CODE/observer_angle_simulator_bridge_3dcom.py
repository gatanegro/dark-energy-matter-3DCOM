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
plt.subplots_adjust(bottom=0.35, left=0.1, right=0.9)

initial_theta_obs = 0
angle_threshold = np.pi / 12  # Visibility threshold

# Initialize scatter plot with proper data structure
x_coords, y_coords, z_coords = zip(*[(x, y, z) for x, y, z, *_ in nodes])
sc = ax.scatter(x_coords, y_coords, z_coords, c='gray', s=20)

# Initialize global variable for export data
last_visible_export = []

# Slider for observer angle
ax_angle = plt.axes([0.25, 0.25, 0.5, 0.03])
slider_angle = Slider(ax_angle, 'Observer Angle (°)', 0, 360, valinit=initial_theta_obs)

# Text field for outputs - positioned to avoid overlap
bridge_text = plt.figtext(0.1, 0.02, "", fontsize=9, wrap=True, 
                         verticalalignment='bottom', bbox=dict(boxstyle="round,pad=0.3", 
                         facecolor="lightgray", alpha=0.8))

# Button to save visible data
ax_button = plt.axes([0.8, 0.15, 0.15, 0.05])
button_save = Button(ax_button, 'Save Visible Nodes')

# --- Update Function ---
def update(val):
    global last_visible_export
    
    theta_obs = np.radians(slider_angle.val)
    visible_coords = []
    colors = []
    output_text = ""
    last_visible_export = []

    for x, y, z, theta, layer, seed, value in nodes:
        diff = abs(theta - theta_obs)
        diff = min(diff, 2 * np.pi - diff)

        visible_coords.append([x, y, z])
        
        if diff < angle_threshold:
            colors.append('red')
            R = bridge_formula(layer)
            output_text += f"n={layer}, seed={seed}, val={value} → R={R:.2e} m\n"
            last_visible_export.append((layer, seed, value, R))
        else:
            colors.append('gray')

    # Update scatter plot data properly
    visible_coords = np.array(visible_coords)
    sc._offsets3d = (visible_coords[:, 0], visible_coords[:, 1], visible_coords[:, 2])
    sc.set_color(colors)
    
    # Update text with proper formatting
    if len(output_text) > 500:  # Truncate if too long
        lines = output_text.split('\n')
        output_text = '\n'.join(lines[:10]) + f"\n... and {len(lines)-10} more nodes"
    
    bridge_text.set_text(output_text)
    fig.canvas.draw_idle()

# --- Save Function ---
def save_visible_nodes(event):
    try:
        with open("visible_nodes.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Layer", "Seed", "Value", "Bridge_Radius_m"])
            for row in last_visible_export:
                writer.writerow(row)
        print(f"Visible nodes saved to 'visible_nodes.csv' ({len(last_visible_export)} nodes)")
        
        # Update button text temporarily to show success
        button_save.label.set_text('Saved!')
        fig.canvas.draw_idle()
        
        # Reset button text after 2 seconds
        fig.canvas.start_event_loop(0.001)  # Small delay
        button_save.label.set_text('Save Visible Nodes')
        fig.canvas.draw_idle()
        
    except Exception as e:
        print(f"Error saving file: {e}")

# Connect event handlers
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
update(initial_theta_obs)

# Show the plot
plt.show()


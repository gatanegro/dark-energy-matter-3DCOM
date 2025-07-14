import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D

# Constants
HQS = 0.235
LZ = 1.23498228
alpha = 0.0072973525693
phi_ref = np.pi / 2 + np.pi / 100  # ~91.8°

# Collatz generation
def generate_collatz_sequence(n):
    sequence = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        sequence.append(n)
    return sequence

# Octave math
def reduce_to_single_digit(value):
    return (value - 1) % 9 + 1

def map_to_octave(value, layer):
    angle = (value / 9) * 2 * np.pi
    x = np.cos(angle) * (layer + 1)
    y = np.sin(angle) * (layer + 1)
    return x, y, angle

# Build dataset
collatz_data = {n: generate_collatz_sequence(n) for n in range(1, 21)}
stack_spacing = 1.0

# Prepare plot
fig = plt.figure(figsize=(14, 12))
ax = fig.add_subplot(111, projection='3d')

# Gather global curvature data - FIXED: Initialize properly
curvature_errors = []
all_points_plotted = 0

# Plot sequences
for number, sequence in collatz_data.items():
    x_vals, y_vals, z_vals, color_vals = [], [], [], []

    for layer, value in enumerate(sequence):
        reduced = reduce_to_single_digit(value)
        x, y, theta = map_to_octave(reduced, layer)
        z = layer * stack_spacing

        phi_error = abs(theta - phi_ref)
        # FIXED: Normalize to [0, π] to avoid wrap-around issues
        phi_error = min(phi_error, 2*np.pi - phi_error)
        curvature_errors.append(phi_error)

        x_vals.append(x)
        y_vals.append(y)
        z_vals.append(z)
        color_vals.append(phi_error)

    # FIXED: Only plot if we have data and increment counter
    if len(x_vals) > 0:
        scatter = ax.scatter(x_vals, y_vals, z_vals, c=color_vals, cmap='coolwarm', s=20)
        all_points_plotted += len(x_vals)
        
        # Optional: line connector
        ax.plot(x_vals, y_vals, z_vals, alpha=0.4)

# FIXED: Only create colorbar if we have data
if len(curvature_errors) > 0 and all_points_plotted > 0:
    norm = Normalize(vmin=min(curvature_errors), vmax=max(curvature_errors))
    mappable = plt.cm.ScalarMappable(norm=norm, cmap='coolwarm')
    mappable.set_array(curvature_errors)
    cbar = plt.colorbar(mappable, ax=ax, shrink=0.6, pad=0.1)
    cbar.set_label("Recursive Phase Curvature Residual (radians)", fontsize=10)

# Axes and title
ax.set_title("3DCOM Collatz-Octave Recursion with Dark Energy Residual Overlay", fontsize=14)
ax.set_xlabel("X (Octave Phase)")
ax.set_ylabel("Y (Octave Phase)")
ax.set_zlabel("Z (Recursion Depth)")

# FIXED: Calculate and set proper axis limits
if all_points_plotted > 0:
    # Recalculate all coordinates to get proper limits
    all_x, all_y, all_z = [], [], []
    for number, sequence in collatz_data.items():
        for layer, value in enumerate(sequence):
            reduced = reduce_to_single_digit(value)
            x, y, theta = map_to_octave(reduced, layer)
            z = layer * stack_spacing
            all_x.append(x)
            all_y.append(y)
            all_z.append(z)
    
    max_radius = max(np.sqrt(np.array(all_x)**2 + np.array(all_y)**2))
    max_z = max(all_z)
    
    ax.set_xlim([-max_radius*1.1, max_radius*1.1])
    ax.set_ylim([-max_radius*1.1, max_radius*1.1])
    ax.set_zlim([0, max_z*1.1])
else:
    # Default limits if no data
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_zlim([0, 10])

# Final output: global Omega_Lambda
omega_lambda = HQS * (phi_ref + LZ + np.sqrt(alpha))
print(f"Global Ω_Λ Estimate from Recursive Curvature: {omega_lambda:.6f}")

# FIXED: Proper plot saving and display
plt.tight_layout()

# Save to current directory to avoid path issues
plt.savefig('Dark Energy 3DCOM.png', dpi=300, bbox_inches='tight')
print(f"Plot saved as 'Dark Energy 3DCOM.png'")

plt.show()

# FIXED: Proper summary with actual counts
print(f"Total data points plotted: {all_points_plotted}")
print(f"Total curvature errors calculated: {len(curvature_errors)}")
print(f"Number of sequences: {len(collatz_data)}")

if len(curvature_errors) > 0:
    print(f"Curvature error range: [{min(curvature_errors):.4f}, {max(curvature_errors):.4f}]")
    print(f"Mean curvature error: {np.mean(curvature_errors):.4f}")
else:
    print("WARNING: No curvature errors calculated - check data generation!")


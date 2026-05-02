import matplotlib

matplotlib.use('TkAgg')  # Set backend to TkAgg for interactive display
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import math

# Set font style to Arial for all text
plt.rcParams['font.family'] = 'Arial'

# Define the path to the input CSV file and output folder
DATA_FILE_PATH = r"data\titre.csv"
OUTPUT_FOLDER = r"output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Create output folder if it doesn't exist
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "yield_plot.png")


# Load and clean the data
def load_and_clean_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Clean data: remove empty rows and invalid yield values
        df = df.dropna()
        df = df[df['Yield'].apply(lambda x: isinstance(x, (int, float)) and not np.isnan(x))]
        # Ensure Time is numeric
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df = df.dropna(subset=['Time'])
        # Ensure marker, facecolor, alpha, xcompensate, and ycompensate_ratio are valid
        df['marker'] = df['marker'].astype(str)
        df['facecolor'] = df['facecolor'].astype(str)
        df['alpha'] = pd.to_numeric(df['alpha'], errors='coerce')
        df['xcompensate'] = pd.to_numeric(df['xcompensate'], errors='coerce')
        df['ycompensate_ratio'] = pd.to_numeric(df['ycompensate_ratio'], errors='coerce')
        df = df.dropna(subset=['alpha', 'xcompensate', 'ycompensate_ratio'])
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


# Plot the data in one figure
def plot_data_figure(df):
    plt.figure(figsize=(17 * 0.393701, 17 * 0.393701))  # Width and height both 17 cm

    for _, row in df.iterrows():
        # Use CSV-defined styles
        marker = row['marker']
        facecolor = row['facecolor']
        alpha = row['alpha']
        xcompensate = row['xcompensate']
        ycompensate_ratio = row['ycompensate_ratio']

        # Convert 'none' or invalid facecolor to None for unfilled
        if pd.isna(facecolor) or facecolor.lower() == 'none':
            facecolor = None
        elif facecolor.lower() == 'white' and alpha == 0.0:
            facecolor = 'white'  # Ensure white with alpha=0 is handled

        # Calculate xytext using xcompensate and ycompensate_ratio
        xytext = (row['Time'] + xcompensate, row['Yield'] * (1 + ycompensate_ratio))

        # Plot scatter point with black outline (width 0.5), reduced size
        plt.scatter(
            row['Time'], row['Yield'],
            marker=marker,
            facecolor=facecolor,
            edgecolor='black',  # Black outline for all symbols
            alpha=alpha,
            s=50,  # Reduced size
            linewidths=0.5,  # Outline width set to 0.5
        )

        # Annotate with product-yield with conditional formatting
        if row['Yield'] < 1:
            yield_text = f"{row['Yield']:.1f}"  # One decimal place for yields < 1
        else:
            yield_text = f"{int(row['Yield'])}"  # Integer for yields >= 1
        plt.annotate(
            f"{row['Product']}-{yield_text}",
            xy=(row['Time'], row['Yield']),
            xytext=xytext,
            textcoords='data',
            arrowprops=dict(arrowstyle='-', color='black', linewidth=0.5),
            fontsize=7,  # Font size set to 7
            color='black'  # Annotation text in black
        )

    # Customize plot with font size 7
    plt.xlabel('Time (Year)', fontsize=7, color='black')
    plt.ylabel('Productivity (mg g-1 DCW)', fontsize=7, color='black')  # Changed to avoid superscript minus issue

    # Set y-axis to logarithmic scale due to wide range of yields
    plt.yscale('log')
    plt.ylim(0.1, 1000)  # Adjusted for mg g^-1 DCW (0.32 to 356.976744)

    # Set axis colors to black and remove top/right outlines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.tick_params(axis='x', colors='black', labelsize=7)
    ax.tick_params(axis='y', colors='black', labelsize=7)

    # Adjust layout
    plt.tight_layout()

    # Save the figure to the output folder
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    return plt.gcf()  # Return the figure for reference


# Plot the legend in a separate figure
def plot_legend_figure(df):
    fig_legend = plt.figure(figsize=(17 * 0.393701, 2 * 0.393701))  # Smaller height for legend
    unique_chassis = df['Chassis'].unique()

    for i, chassis in enumerate(unique_chassis):
        # Use the first occurrence of marker, facecolor, and alpha for this chassis
        sample_row = df[df['Chassis'] == chassis].iloc[0]
        marker = sample_row['marker']
        facecolor = sample_row['facecolor']
        alpha = sample_row['alpha']

        # Override facecolor to white for legend
        facecolor = 'white'
        alpha = 1.0  # Ensure full opacity for legend visibility

        if pd.isna(facecolor) or facecolor.lower() == 'none':
            facecolor = None
        elif facecolor.lower() == 'white' and alpha == 0.0:
            facecolor = 'white'

        # Create a dummy plot to generate legend entries
        plt.scatter([], [], marker=marker, facecolor=facecolor, edgecolor='black', alpha=alpha,
                    label=chassis, s=50, linewidths=0.5)  # Match outline width

    # Customize legend without title, with italic font
    legend = plt.legend(loc='center', ncol=4, fontsize=7, frameon=False)
    for text in legend.get_texts():
        text.set_style('italic')  # Set legend text to italic

    plt.axis('off')  # Hide axes
    plt.tight_layout()

    # Save the legend figure
    legend_output = os.path.join(OUTPUT_FOLDER, "legend_plot.png")
    plt.savefig(legend_output, dpi=300, bbox_inches='tight')
    return fig_legend


# Main execution
if __name__ == '__main__':
    df = load_and_clean_data(DATA_FILE_PATH)
    if df is not None:
        data_fig = plot_data_figure(df)
        legend_fig = plot_legend_figure(df)
        plt.show()  # Display both figures
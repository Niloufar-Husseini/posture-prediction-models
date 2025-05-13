import pandas as pd
import numpy as np
import os
from scipy import interpolate
from pathlib import Path

def calculate_new_origin(df):
    """Calculate mean midpoint between LHEE (X.31/Y.31/Z.32) and RHEE (X.37/Y.37/Z.37)"""
    lhee_mean = np.array([
        df['X.Subj1:LHEE'].mean(),
        df['Y.Subj1:LHEE'].mean(),
        df['Z.Subj1:LHEE'].mean()
    ])
    
    rhee_mean = np.array([
        df['X.Subj1:RHEE'].mean(),
        df['Y.Subj1:RHEE'].mean(),
        df['Z.Subj1:RHEE'].mean()
    ])
    
    return (lhee_mean + rhee_mean) / 2

def shift_coordinates(df, origin):
    """Shift all coordinates to new origin (handles X.##, Y.##, Z.## columns)"""
    df_shifted = df.copy()
    
    for col in df.columns:
        if col.startswith(('X', 'Y')):
            axis = col[0]  # X, Y, or Z
            df_shifted[col] = df[col] - origin['XY'.index(axis)]
    
    return df_shifted

def reorder_and_clean_columns(df):
    """Remove first two columns, drop specific columns, and reorder as Xs, Ys, then Zs"""
    # Step 1: Remove the first two columns
    # df = df.iloc[:, 2:]
    
    # Step 2: Drop specified empty columns
    # columns_to_drop = [
    #     'X.39', 'Y.39', 'Z.39',
    #     'X.40', 'Y.40', 'Z.40',
    #     'X.41', 'Y.41', 'Z.41',
    #     'X.42', 'Y.42', 'Z.42'
    # ]
    # df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Step 3: Reorder columns by Xs, then Ys, then Zs
    x_cols = [col for col in df.columns if col.startswith('X')]
    y_cols = [col for col in df.columns if col.startswith('Y')]
    z_cols = [col for col in df.columns if col.startswith('Z')]

    new_order = x_cols + y_cols + z_cols
    df = df[new_order]

    return df

def resample_to_101(df):
    """Resample dataframe to exactly 101 frames"""
    original_length = len(df)
    new_index = np.linspace(0, original_length-1, 101)
    
    resampled = {}
    for col in df.columns:
        if col in ['Frame', 'Sub Frame']:
            if col == 'Frame':
                resampled[col] = np.arange(1, 102)
            else:
                resampled[col] = np.zeros(101)
        else:
            f = interpolate.interp1d(np.arange(original_length), df[col], kind='linear')
            resampled[col] = f(new_index)
    
    return pd.DataFrame(resampled)

def process_file(input_path, output_folder):
    """Process a single mocap file with consistent column naming"""
    try:
        # Read data (skip 3 header lines)
        df = pd.read_csv(input_path)
        # print(df)

        # 1. Calculate new origin
        origin = calculate_new_origin(df)
        print(origin)

        # 2. Shift coordinates
        df_shifted = shift_coordinates(df, origin)

        # 3. Reorder and clean columns
        df_cleaned = reorder_and_clean_columns(df_shifted)

        # 4. Resample to 101 frames
        df_resampled = resample_to_101(df_cleaned)

        # Save results
        output_path = os.path.join(output_folder, f"processed_{os.path.basename(input_path)}")
        df_resampled.to_csv(output_path, index=False)
        
        return True, output_path
    
    except Exception as e:
        return False, str(e)

def process_all(input_dir, output_dir='processed'):
    """Process all CSV files in input directory"""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    for file in Path(input_dir).glob('*.csv'):
        success, msg = process_file(file, output_dir)
        if success:
            print(f"Processed {file.name} -> {msg}")
            results.append(msg)
        else:
            print(f"Failed {file.name}: {msg}")
    
    print(f"\nCompleted: {len(results)} files processed")
    return results

if __name__ == "__main__":
    # Example usage
    input_directory = 'extracted_frames'  # Folder with your CSV files
    process_all(input_directory)

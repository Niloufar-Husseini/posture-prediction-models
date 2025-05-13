import pandas as pd
import os

def extract_frames_based_on_excel(excel_file, input_folder='', output_folder='extracted_frames'):
    """
    Extract frames from motion capture CSV files based on frame ranges specified in an Excel file.
    Handles the special format of motion capture data files with metadata headers.
    
    Args:
        excel_file (str): Path to the Excel file containing frame ranges
        input_folder (str): Folder where input CSV files are located
        output_folder (str): Folder where extracted CSV segments will be saved
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Read the Excel file
    df_ranges = pd.read_excel(excel_file)
    
    # Process each row in the Excel file
    for index, row in df_ranges.iterrows():
        csv_file = os.path.join(input_folder, f"{row['File name']}.csv")
        start_frame = row['start frame']
        stop_frame = row['stop frame']
        technique = row['technique']
        hand = row['hand']
        
        # Generate output filename
        output_filename = f"{row['File name']}_frames_{start_frame}-{stop_frame}_technique_{technique}_hand_{hand}.csv"
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            # Read the CSV file while preserving the header structure
            with open(csv_file, 'r') as f:
                # Read the first 3 lines (metadata and column headers)
                header_lines = [f.readline() for _ in range(3)]
            
            # Read the actual data starting from row 4 (0-indexed row 3)
            # Skip the first 3 rows and use the 4th row as header
            df_csv = pd.read_csv(csv_file, skiprows=3, header=0)
            
            # Extract the specified frames (adjusting for 1-based vs 0-based indexing)
            extracted_frames = df_csv.iloc[start_frame-1:stop_frame]
            
            # Save to new CSV file with original header structure
            with open(output_path, 'w') as f:
                # Write the original header lines
                f.writelines(header_lines)
                # Write the extracted frames
                extracted_frames.to_csv(f, index=False, lineterminator='\n')
            
            print(f"Successfully extracted frames {start_frame}-{stop_frame} from {csv_file} to {output_path}")
            
        except FileNotFoundError:
            print(f"Error: CSV file not found - {csv_file}")
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")

# Example usage
if __name__ == "__main__":
    extract_frames_based_on_excel('frames.xlsx', r"C:\Niloofar\SCR\posture-prediction-models-main\external_data_processing\raw data\s8")
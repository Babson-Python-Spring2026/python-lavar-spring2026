class DataHandler:
    def read_csv(self, file_path):
        import pandas as pd
        return pd.read_csv(file_path)

    def write_json(self, data, output_path):
        import json
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
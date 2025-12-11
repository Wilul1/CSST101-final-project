import pandas as pd

df = pd.read_csv('vehicle_dataset.csv')
print(f'Total columns: {len(df.columns)}\n')
print('All columns in vehicle_dataset.csv:')
print('=' * 60)
for i, col in enumerate(df.columns, 1):
    print(f'{i:2d}. {col}')

print('\n' + '=' * 60)
print(f'\nTotal records: {len(df)}')
print(f'\nRequired ML columns present:')
print(f'  [OK] category: {"category" in df.columns}')
print(f'  [OK] description: {"description" in df.columns}')
print(f'  [OK] location: {"location" in df.columns}')
print(f'  [OK] priority: {"priority" in df.columns}')


import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

pd.set_option('display.max_columns', 13, 'display.max_colwidth', 11,
              'display.min_rows', 20, 'display.max_rows', 30, 'display.width', 1000)

# Function to calculate he weighted average of a number Series without NaN values
def average_for_number_column(Series):
    return(sum(Series)/len(Series))

# Function to calculate the weighted average of a string Series without NaN values, reindexed with first integers
def weighted_average_for_string_column(Series):
    Series_value_counts = Series.value_counts()
    Series_value_counts = Series_value_counts.reset_index(drop = True)
    sum_prod = 0
    for i in range(len(Series_value_counts)):
        sum_prod += Series_value_counts.iloc[i] * i
        #sum_prod += Series_value_counts.iloc[i] * (i + 1)
    weighted_average = sum_prod / sum(Series_value_counts)
    return weighted_average

# Load the data, and separate the target y
train_path = './input/train.csv'
train_data = pd.read_csv(train_path)
y = train_data.SalePrice

# Create X
features_selected = ['MSSubClass', 'MSZoning', 'LotFrontage', 'LotArea', 'Street', 'Alley', 'LotShape', 'LandContour',
 'Utilities', 'LotConfig', 'LandSlope', 'Neighborhood', 'Condition1', 'Condition2', 'BldgType', 'HouseStyle',
 'OverallQual', 'OverallCond', 'YearBuilt', 'YearRemodAdd', 'RoofStyle', 'RoofMatl', 'Exterior1st', 'Exterior2nd',
 'MasVnrType', 'MasVnrArea', 'ExterQual', 'ExterCond', 'Foundation', 'BsmtQual', 'BsmtCond', 'BsmtExposure',
 'BsmtFinType1', 'BsmtFinSF1', 'BsmtFinType2', 'BsmtFinSF2', 'BsmtUnfSF', 'TotalBsmtSF', 'Heating', 'HeatingQC',
 'CentralAir', 'Electrical', '1stFlrSF', '2ndFlrSF', 'LowQualFinSF', 'GrLivArea', 'BsmtFullBath', 'BsmtHalfBath',
 'FullBath', 'HalfBath', 'BedroomAbvGr', 'KitchenAbvGr', 'KitchenQual', 'TotRmsAbvGrd', 'Functional', 'Fireplaces',
 'FireplaceQu', 'GarageType', 'GarageYrBlt', 'GarageFinish', 'GarageCars', 'GarageArea', 'GarageQual', 'GarageCond',
 'PavedDrive', 'WoodDeckSF', 'OpenPorchSF', 'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea', 'PoolQC',
 'Fence', 'MiscFeature', 'MiscVal', 'MoSold', 'YrSold', 'SaleType', 'SaleCondition']

# Select columns corresponding to features
X = train_data[features_selected]

# Warning some features columns contain string values. We have to convert them to numbers.
# Avoid warning when changing values of dataframe:
pd.options.mode.chained_assignment = None

### Replace NAN by average in columns who contain number values
# Select number columns
number_features_selected = [column_name for column_name in features_selected if (X.loc[:, column_name].dtype == 'int64' or X.loc[:, column_name].dtype == 'float64')]
print(number_features_selected)
# Fill columns
# Function to fill 'NaN' entries by average of the other values in numbers columns
def fill_NaN_by_average_in_all_numbers_columns(X, number_features_selected):
    for column_name in number_features_selected:
        # Copy the column without NaN entries before changes to calculate the weighted average later
        column_without_NaN_entries = X.loc[:, column_name].dropna()
        X.loc[:, column_name] = X.loc[:, column_name].fillna(average_for_number_column(column_without_NaN_entries) * 1)
fill_NaN_by_average_in_all_numbers_columns(X, number_features_selected)
### Replace string by numbers in columns who contain object values
# Select object columns
string_features_selected = [column_name for column_name in features_selected if X.loc[:, column_name].dtype == object]
print(string_features_selected)
# Function to convert columns in a DataFrame who contain string values using directories and save these
# For each use, this one save dictionary used into the list below in order to reuse further
list_of_dict_used = []
def convert_to_numbers_and_save_dict_used(column_name, DataFrame, list_of_dict):
    # Copy the column without NaN entries before changes to calculate the weighted average later
    column_without_NaN_entries = DataFrame.loc[:, column_name].dropna()
    # Fill "NaN" entries with "Unknown"
    DataFrame.loc[:, column_name] = DataFrame.loc[:, column_name].fillna("Unknown")
    column_value_counts = DataFrame.loc[:, column_name].value_counts()
    #print(column_value_counts)
    # Warning. We have to convert column_value_counts_index into list to find the place of each string value in its index:
    column_value_counts_index = column_value_counts.index.tolist()
    column_dict = {string_value: column_value_counts_index.index(string_value) for string_value in column_value_counts_index}
    # We assure the key "Unknown" is in dictionary to avoid empty entries problems with test_data during submission
    # We give to the "Unknown" key the value of weighted average of values in the new dictionary
    print(column_dict)
    # Calculate the weighted average
    column_dict["Unknown"] = weighted_average_for_string_column(column_without_NaN_entries) * 0.4
    print(column_dict)
    DataFrame.loc[:, column_name] = DataFrame.loc[:, column_name].map(lambda p: column_dict[p])
    list_of_dict = list_of_dict.append(column_dict)

# Convert columns
for column_name in string_features_selected:
    convert_to_numbers_and_save_dict_used(column_name, X, list_of_dict_used)

# Split X and y into validation and training data
train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)

# Define and fit a random forest model, make validation predictions and calculate mean absolute error
model_default = RandomForestRegressor(random_state=1)
model_default.fit(train_X, train_y)
model_default_val_preds = model_default.predict(val_X)
default_val_mae = mean_absolute_error(model_default_val_preds, val_y)
print("\nValidation MAE for Model with no value of max_leaf_node: {:,.0f}\n".format(default_val_mae))

### Recalculate MAE for a new list_of_dict_used
# Functions used
# Function to convert a string columns with a new 'list_of_dict_used'
def convert_string_column_into_numbers_using_dict_in_list_of_dict_used(column_name, DataFrame, dict):
    # Fill "NaN" entries with "Unknown"
    DataFrame.loc[:, column_name] = DataFrame.loc[:, column_name].fillna("Unknown")
    DataFrame.loc[:, column_name] = DataFrame.loc[:, column_name].map(lambda p: dict[p])
# Function to convert all string columns with a new 'list_of_dict_used'
def convert_string_columns_into_numbers_using_list_of_dict_used(X, list_of_dict_used):
    i = 0
    for column_name in string_features_selected:
        convert_string_column_into_numbers_using_dict_in_list_of_dict_used(column_name, X, list_of_dict_used[i])
        i += 1
# Function to recalculate MAE with an other list_of_dict_used
def calculate_MAE(X, list_of_dict_used):
    # Restart at the beginning for X
    X = train_data[features_selected]
    # Fill columns
    fill_NaN_by_average_in_all_numbers_columns(X, number_features_selected)
    # Convert columns with the new dict 'list_of_dict_used'
    convert_string_columns_into_numbers_using_list_of_dict_used(X, list_of_dict_used)
    # Split X and y into validation and training data
    train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)
    # Define and fit a random forest model, make validation predictions and calculate mean absolute error
    model_default = RandomForestRegressor(random_state=1)
    model_default.fit(train_X, train_y)
    model_default_val_preds = model_default.predict(val_X)
    default_val_mae = mean_absolute_error(model_default_val_preds, val_y)
    #print("\nNew validation MAE for Model with no value of max_leaf_node: {:,.0f}\n".format(default_val_mae))
    return(default_val_mae)

# Establish new list_of_dict_used and recalculate MAE for changes of number order in 'n' consecutive columns
old_val_mae = default_val_mae

#for n in range(len(list_of_dict_used), -1, -1):
#for n in [40, 35, 31, 29, 28, 27, 24, 22, 3, 2, 1]:
for n in range(3, 0, -1):
    print('\n', len(list_of_dict_used) - n, 'opérations sur', n + 1, 'colonnes adjacentes')
    for i in range(len(list_of_dict_used) - n):
        print(i + 1, end = ' ')
        for j in range(n):
            for key in list_of_dict_used[i + j]:
                list_of_dict_used[i + j][key] = len(list_of_dict_used[i + j]) - list_of_dict_used[i + j][key] - 1
        new_val_mae = calculate_MAE(X, list_of_dict_used)
        if new_val_mae >= old_val_mae:
            for j in range(n):
                for key in list_of_dict_used[i + j]:
                    list_of_dict_used[i + j][key] = len(list_of_dict_used[i + j]) - list_of_dict_used[i + j][key] - 1
        else:
            print("\nNew validation MAE for Model with no value of max_leaf_node: {:,.0f}\n".format(new_val_mae))
            old_val_mae = new_val_mae

for i in range(len(list_of_dict_used)):
    print(list_of_dict_used[i])



# Fit Model Using All Data
final_model = RandomForestRegressor(random_state=1)
final_model.fit(X, y)

# Get "test" data to make final prediction
test_path = './input/test.csv'
test_data = pd.read_csv(test_path)
test_X = test_data[features_selected]
# Fill and convert columns selected as before
fill_NaN_by_average_in_all_numbers_columns(test_X, number_features_selected)
convert_string_columns_into_numbers_using_list_of_dict_used(test_X, list_of_dict_used)
print(test_X.head())
# make predictions which we will submit.
test_preds = final_model.predict(test_X)

# Generate a submission
output = pd.DataFrame({'Id': test_data.Id, 'SalePrice': test_preds})
output.to_csv('submission8.csv', index=False)
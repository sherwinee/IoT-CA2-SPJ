def predict_danger(df):
    import pandas as pd
    from sklearn.decomposition import PCA
    from joblib import load
    from sklearn import svm
    from math import sqrt, ceil

    # Change column names to match
    df = df.rename({'bookingid': 'bookingID', 'accuracy': 'Accuracy', 'bearing': 'Bearing', 'speed': 'Speed'}, axis=1)
    print('\n==============================')
    print(df.info())
    print(df.isnull().any())
    print('==============================\n')

    # Read in model
    model = load("model_svm.joblib")

    # Make the final features DF
    label_df = pd.DataFrame()
    unique_ids = list(df['bookingID'].unique())
    label_df['bookingID'] = unique_ids
    label_df = label_df.sort_values(by='bookingID', ascending=True)

    # Get Net Acceleration
    df['acceleration_xyz'] = df.apply(lambda x: sqrt((x['acceleration_x'] ** 2) + (x['acceleration_y'] ** 2) + (x['acceleration_z'] ** 2)), axis=1)

    # Use PCA to process Gyro data
    gyro_pca = PCA(n_components=1).fit(df.loc[:, ['gyro_x', 'gyro_y', 'gyro_z']])
    gyro_pca.explained_variance_ratio_
    df['gyro'] = gyro_pca.transform(df.loc[:, ('gyro_x', 'gyro_y', 'gyro_z')])
    df.drop(['gyro_x', 'gyro_y','gyro_z'], axis=1, inplace=True)

    # Functions for processing
    def get_percentile(values, percentile):
        values = sorted(values)
        index = (float(percentile) / 100) * len(values)
        if index.is_integer():
            index = int(index)
            value = (values[index - 1] + values[index]) / 2
        else:
            value = values[ceil(index - 1)]
        return value

    def get_mean(values):
        return sum(values) / len(values)

    # Get full data from each ID
    speed_dict = {}
    accel_dict = {}
    gyro_dict = {}
    counter=0
    for index, row in df.iterrows():
        bid = row['bookingID']
        speed = float(row['Speed'])
        accel = float(row['acceleration_xyz'])
        gyro = float(row['gyro'])
        if bid in speed_dict:
            speed_dict[bid].append(speed)
            accel_dict[bid].append(accel)
            gyro_dict[bid].append(gyro)
        else:
            speed_dict[bid] = [speed]
            accel_dict[bid] = [accel]
            gyro_dict[bid] = [gyro]

    # Add Statistical Features
    # Speed Statistics
    label_df['90pct_speed'] = label_df.apply(lambda x: get_percentile(speed_dict[x['bookingID']].copy(), 90), axis=1)
    label_df['median_speed'] = label_df.apply(lambda x: get_percentile(speed_dict[x['bookingID']].copy(), 50), axis=1)
    label_df['mean_speed'] = label_df.apply(lambda x: get_mean(speed_dict[x['bookingID']].copy()), axis=1)
    label_df['max_speed'] = label_df.apply(lambda x: max(speed_dict[x['bookingID']].copy()), axis=1)

    # Acceleration Statistics
    label_df['90pct_acceleration'] = label_df.apply(lambda x: get_percentile(accel_dict[x['bookingID']].copy(), 90), axis=1)
    label_df['median_acceleration'] = label_df.apply(lambda x: get_percentile(accel_dict[x['bookingID']].copy(), 50), axis=1)
    label_df['mean_acceleration'] = label_df.apply(lambda x: get_mean(accel_dict[x['bookingID']].copy()), axis=1)
    label_df['max_acceleration'] = label_df.apply(lambda x: max(accel_dict[x['bookingID']].copy()), axis=1)

    # Gyroscope Statistics
    label_df['75pct_gyro'] = label_df.apply(lambda x: get_percentile(gyro_dict[x['bookingID']].copy(), 75), axis=1)
    label_df['median_gyro'] = label_df.apply(lambda x: get_percentile(gyro_dict[x['bookingID']].copy(), 50), axis=1)
    label_df['25pct_gyro'] = label_df.apply(lambda x: get_percentile(gyro_dict[x['bookingID']].copy(), 25), axis=1)
    label_df['mean_gyro'] = label_df.apply(lambda x: get_mean(gyro_dict[x['bookingID']].copy()), axis=1)
    label_df['max_gyro'] = label_df.apply(lambda x: max(gyro_dict[x['bookingID']].copy()), axis=1)

    # Backup
    # Acceleration Statistics
    # label_df['75pct_acceleration'] = label_df.apply(lambda x: get_percentile(accel_dict[x['bookingID']].copy(), 75), axis=1)
    # label_df['median_acceleration'] = label_df.apply(lambda x: get_percentile(accel_dict[x['bookingID']].copy(), 50), axis=1)
    # label_df['25pct_acceleration'] = label_df.apply(lambda x: get_percentile(accel_dict[x['bookingID']].copy(), 25), axis=1)
    # label_df['mean_acceleration'] = label_df.apply(lambda x: get_mean(accel_dict[x['bookingID']].copy()), axis=1)
    # label_df['max_acceleration'] = label_df.apply(lambda x: max(accel_dict[x['bookingID']].copy()), axis=1)

    # Prediction

    df_new = label_df.drop(['bookingID'], axis=1, inplace=False).copy()
    X_test = df_new
    print('before predict')
    predicted = list(model.predict(X_test))
    print('after predict')
    result_df = pd.DataFrame()
    result_df['bookingID'] = label_df['bookingID']
    result_df['label'] = predicted
    result_df.set_index('bookingID', drop=True)

    return result_df

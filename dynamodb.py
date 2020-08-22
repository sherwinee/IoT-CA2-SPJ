#https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-6.html
#https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-7.html
# https://aws.amazon.com/premiumsupport/knowledge-center/create-gsi-dynamodb/
# https://dynobase.dev/dynamodb-python-with-boto3/


def get_data_from_dynamodb():
    try:
            import boto3
            from boto3.dynamodb.conditions import Key, Attr

            table_name = 'mygrabtable'
            print(f"Querying table {table_name}")
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.Table(table_name)

            response = table.scan(
                # ScanFilter={
                #     "bookingid":{
                #         'ComparisonOperator': "GE",
                #         'AttributeValueList': [ {"S":"0.0"}]
                #     }
                # }
            )
            # Tried to use query to get multiple booking ids, but was unable to do so, therefore
            # we decided to use .scan instead to read every item in the table, even though this is inefficient
            # and costly(in real world context), we were unable to get Query to work in time and therefore Scan was used instead
            
            # response = table.query(
            #     #KeyConditionExpression=Key('bookingid').eq('0.0'),
            #     # Add the name of the index you want to use in your query.
            #     IndexName="bookingid-datetime_value-index",
            #     KeyConditionExpression='bookingid = :bookingid AND bookingid > :bookingid',
            #     ExpressionAttributeValues={
            #         ':bookingid': {'S': '0.0'}
            #     },
            #     ScanIndexForward=False,
            #     Limit=10
            # )            

            items = response['Items']

            n=20 # limit to last 20 items
            data = items[:n]
            data_reversed = data[::-1]

            return data_reversed

    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])


if __name__ == "__main__":
    get_data_from_dynamodb()

import boto3
import pandas as pd
from datetime import date, timedelta


def fetch_aws_cost_data(days=7):
    client = boto3.client("ce", region_name="us-east-1")

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d")
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {
                "Type": "DIMENSION",
                "Key": "SERVICE"
            }
        ]
    )

    rows = []

    for result in response["ResultsByTime"]:
        current_date = result["TimePeriod"]["Start"]

        for group in result["Groups"]:
            service = group["Keys"][0]
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])

            rows.append({
                "date": current_date,
                "service": service,
                "team": "Unknown",
                "project": "Unknown",
                "environment": "Unknown",
                "resource_id": "AWS-CostExplorer",
                "usage": 1,
                "cost": cost,
                "region": "global",
                "owner": "Unknown"
            })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])

    return df
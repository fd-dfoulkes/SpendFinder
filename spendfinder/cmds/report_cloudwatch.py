import dataclasses

import boto3
import math


def round_currency_up(value):
    return math.ceil(value * 100) / 100


# Classes

@dataclasses.dataclass
class CloudWatchLogStats:
    size_bytes: int
    arn: str
    retention_in_days: str
    created_time: str
    region: str

    def get_size_in_gb(self):
        return self.size_bytes / 1024 / 1024 / 1024

    def get_cost(self):
        return round_currency_up(self.get_size_in_gb() * 0.03)


def regions():
    return ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ap-south-1", "ap-northeast-1", "ap-northeast-2",
            "ap-southeast-1", "ap-southeast-2", "ca-central-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3",
            "eu-north-1", "sa-east-1"]


## Runtime method

def metrics_costs(profile):
    # get the total amount of custom metrics
    custom_metrics_count = 0
    for region in regions():
        session = boto3.Session(profile_name=profile, region_name=region)
        client = session.client("cloudwatch")
        response = client.list_metrics()
        # Paginate through the results
        while True:
            for metric in response["Metrics"]:
                if not metric["Namespace"].startswith("AWS/"):
                    custom_metrics_count += 1
            if "NextToken" in response:
                response = client.list_metrics(NextToken=response["NextToken"])
            else:
                break
    return custom_metrics_count, round_currency_up(custom_metrics_count * 0.3)


def logs_costs(profile):
    results = []
    for region in regions():
        session = boto3.Session(profile_name=profile, region_name=region)
        client = session.client("logs")
        response = client.describe_log_groups()
        # Paginate through the results
        while True:
            log_groups = response["logGroups"]
            for log_group in log_groups:
                arn = log_group["arn"]
                size_bytes = log_group["storedBytes"]
                creation_time = log_group["creationTime"]
                if "retentionInDays" in log_group:
                    retention_in_days = str(log_group["retentionInDays"])
                else:
                    retention_in_days = "No retention policy"
                results.append(CloudWatchLogStats(size_bytes, arn, retention_in_days, creation_time, region))
            if "nextToken" in response:
                response = client.describe_log_groups(nextToken=response["nextToken"])
            else:
                break
    return results

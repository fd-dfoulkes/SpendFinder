import click
import os
import yaml
import spendfinder.cmds.ec2 as ec2
import boto3
from spendfinder.cmds.report_cloudwatch import logs_costs as logs
from spendfinder.cmds.report_cloudwatch import metrics_costs as metrics

@click.group(chain=True, help="Cloudwatch costs and usage")
def aws_cloudwatch():
    pass


# identify cloudwatch cost ownership

@aws_cloudwatch.command()
@click.option("--output", help="Output file for the report")
@click.option("--profile", help="AWS profile to use")
@click.option("--service", help="which cw service to report on")
def cloudwatch(output, service, profile):

    if service == "logs":
        if output:
            if not output.endswith(".csv"):
                click.echo("Error: Output file must be a CSV file.")
                exit()

            usage_report = logs(profile)
            usage_report_sorted = sorted(usage_report, key=lambda item: item.get_cost(), reverse=True)


            for item in usage_report_sorted:
                click.echo(f"ARN: {item.arn}, Size: {item.get_size_in_gb()} GB, Cost: ${item.get_cost()}, Retention: {item.retention_in_days}, Created: {item.created_time}, Region: {item.region}")

            with open(output, "w") as f:
                f.write("ARN,Size,Retention,Cost,Created,Region\n")
                for item in usage_report_sorted:
                    f.write(f"{item.arn},{item.get_size_in_gb()},{item.retention_in_days},{item.get_cost()},{item.created_time},{item.region}\n")

    if service == "metrics":
        click.echo("Please wait, this can take a while...")
        num_of_metrics, cost = metrics(profile)
        click.clear()
        click.echo(f" total of {num_of_metrics} metrics costing a monthly total of ${cost}")

# identify ec2 instances which are on with no traffic.


# identify S3 buckets with large amounts of storage.


# identify EBS instances that are not GP3


# identify Snapshots that have existed for over 90 days


# identify S3 buckets that do not have lifecycle policies.


# identify idle load balancers.

cli = click.CommandCollection(sources=[aws_cloudwatch])

if __name__ == "__main__":
    cli()


import csv
import re
from pathlib import Path


class Base_Cloud:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def parse_csv(self):
        with open(self.path, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            instance_list = [self.process_row(row) for row in reader]
            return [
                instance
                for instance in instance_list
                if instance["Monthly Cost (on demand)"][:1] == "$"
            ]

    def process_row(self, row):
        return {
            "Name": self.parse_name(row),
            "vCPUs": self.parse_vcpu_count(row),
            "RAM (GB)": self.parse_memory(row),
            "CPU Speed": self.parse_clock_speed(row),
            "Monthly Cost (on demand)": self.parse_monthly_cost(row),
            "Notes": self.parse_notes(row),
            "Cloud": self.name,
        }

    def parse_vcpu_count(self, vcpus_string):
        try:
            return float(vcpus_string.replace("vCPUs", "").replace("vCPU", ""))
        except Exception:
            print(f"ERROR: Could not parse vCPUs string: {vcpus_string}")
            return 0

    def parse_memory(self, ram_string):
        try:
            return float(
                ram_string.replace("GiB", "").replace("Gib", "").replace("GB", "")
            )
        except Exception:
            print(f"ERROR: Could not parse Memory string: {ram_string}")
            return "Unknown"

    def parse_clock_speed(self, cpu_string):
        try:
            if "GHz" in cpu_string:
                return float(cpu_string[: cpu_string.find("GHz")])
            return float(cpu_string)
        except Exception:
            print(f"ERROR: Could not parse Clock Speed string: {cpu_string}")
            return "Unknown"

    def parse_monthly_cost(self, cost_string):
        try:
            return f'${(730 * float(cost_string.replace("$", "").replace("hourly", ""))):.2f}'
        except Exception:
            print(f"ERROR: Could not parse Monthly Cost string: {cost_string}")
            return "Unknown"


class AWS(Base_Cloud):
    def __init__(self, path):
        super().__init__("AWS", path)

    def parse_name(self, row):
        return row["API Name"]

    def parse_vcpu_count(self, row):
        return super().parse_vcpu_count(row["vCPUs"])

    def parse_memory(self, row):
        return super().parse_memory(row["Memory"])

    def parse_clock_speed(self, row):
        return super().parse_clock_speed(row["Clock Speed(GHz)"])

    def parse_monthly_cost(self, row):
        return super().parse_monthly_cost(row["Linux On Demand cost"])

    def parse_notes(self, row):
        notes_string = row["API Name"]
        if notes_string[:1] == "t":
            return "Intended for testing and development"
        if notes_string[:1] == "c":
            return "Compute-optimized"
        if notes_string[:1] == "m":
            return "Memory-optimized"
        if notes_string[:1] == "r":
            return "General Purpose"


class Azure(Base_Cloud):
    def __init__(self, path):
        super().__init__("Azure", path)

    def parse_name(self, row):
        return row["Name"]

    def parse_vcpu_count(self, row):
        return super().parse_vcpu_count(row["vCPUs"])

    def parse_memory(self, row):
        return super().parse_memory(row["Memory"])

    def parse_clock_speed(self, row):
        cpu_string = row["CPU Type"]
        if matches := re.findall(r"(\d+\.\d+) GHz", cpu_string):
            return round(sum(map(float, matches)) / len(matches), 2)
        return cpu_string

    def parse_monthly_cost(self, row):
        return super().parse_monthly_cost(row["Linux Pay As You Go cost"])

    def parse_notes(self, row):
        notes_string = row["Name"]
        if notes_string[:1] in ["A", "B", "D"]:
            return "General-purpose"
        if notes_string[:1] == "F":
            return "Compute-optimized"
        if notes_string[:1] == "E":
            return "Memory-optimized"


class GCP(Base_Cloud):
    def __init__(self, path):
        super().__init__("GCP", path)

    def parse_name(self, row):
        return row["Machine type"]

    def parse_vcpu_count(self, row):
        if row["vCPUs"] == "shared":
            return "shared"
        return super().parse_vcpu_count(row["vCPUs"])

    def parse_memory(self, row):
        return super().parse_memory(row["Memory"])

    def parse_clock_speed(self, row):
        cpu_string = row["CPU Type"]
        if ghz := re.search(r"(\d+\.\d+)GHz", cpu_string):
            return float(ghz[0][:-3])
        return cpu_string

    def parse_monthly_cost(self, row):
        return super().parse_monthly_cost(row["Linux On Demand cost"])

    def parse_notes(self, row):
        notes_string = row["Machine type"]
        if label := re.search(r"(?<=-)[a-z]+", notes_string):
            return label[0]
        return notes_string


class DigitalOcean(Base_Cloud):
    def __init__(self, path):
        super().__init__("Digital Ocean", path)

    def parse_name(self, row):
        return f'{row["Type"]} {row["$/MO"]}'

    def parse_vcpu_count(self, row):
        return super().parse_vcpu_count(row["vCPUs"])

    def parse_memory(self, row):
        return super().parse_memory(row["Memory"])

    def parse_clock_speed(self, row):
        if row["CPU Type"] == "Shared":
            return "Shared"
        return super().parse_clock_speed(row["CPU Type"])

    def parse_monthly_cost(self, row):
        return super().parse_monthly_cost(row["$/HR"])

    def parse_notes(self, row):
        return f'Includes {row["SSD"]} of storage'


def sorter(item):
    if "$" in item["Monthly Cost (on demand)"]:
        return float(item["Monthly Cost (on demand)"][1:])
    return item["Monthly Cost (on demand)"]


def main():
    aws = AWS("data/Amazon EC2 Instance Comparison.csv")
    azure = Azure("data/Microsoft Azure Virtual Machine Comparison.csv")
    gcp = GCP(
        "data/GCPinstances.info - GCP Compute Engine Instance Comparison (by DoiT International).csv"
    )
    digital_ocean = DigitalOcean("data/DO_droplets.csv")

    master_list = (
        aws.parse_csv()
        + azure.parse_csv()
        + gcp.parse_csv()
        + digital_ocean.parse_csv()
    )

    master_list = sorted(
        master_list, key=lambda x: float(x["Monthly Cost (on demand)"][1:])
    )

    with open("data/all_instances.csv", "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=master_list[0].keys())
        writer.writeheader()
        for row in master_list:
            writer.writerow(row)


if __name__ == "__main__":
    main()

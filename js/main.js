import { parse } from './vanillaes_csv/index.min.js'
var instances = [];
const FIELDS = ["Name", "vCPU", "RAM (GB)", "CPU Max Clock (GHz)", "On-demand Monthly", "Reserved Monthly"]
const multipliers = {
    None: {
        file_count: 5,
        file_size: 5,
    },
    Film: {
        file_count: 5,
        file_size: 20,
    },
    Gaming: {
        file_count: 5,
        file_size: 10,
    },
    Strategic: {
        file_count: 10,
        file_size: 1,
    },
    Semiconductor: {
        file_count: 100,
        file_size: 1,
    },
}

var selections = {
    vertical: "",
    users: 5,
    cloud: "AWS",
    commits: 5,
    frequency: 1,
    file_size: 1,
    file_count: 5,
}

$().ready(() => {
    console.log("Ready!");
    initialSetup();
    $("select").on("change", function () {
        if (this.id == "vertical") {
            selections["file_count"] = multipliers[this.value]["file_count"];
            selections["file_size"] = multipliers[this.value]["file_size"];
        }
        selections[this.id] = this.value;
        updateTable();
    });
});

function initialSetup() {
    $.get("data/aws-ec2.csv", (result) => {
        //Get data from csv file
        let data = parse(result);

        for (var i = 1; i < data.length; i++) {
            console.log(data[i]);
            instances.push({});
            for (var j = 0; j < data[i].length; j++) {
                if (isNaN(data[i][j])) {
                    instances[i - 1][data[0][j]] = data[i][j];
                } else if (data[i][j].includes(".")) {
                    instances[i - 1][data[0][j]] = parseFloat(data[i][j]);
                } else {
                    instances[i - 1][data[0][j]] = parseInt(data[i][j]);
                }
            }
        }

        //Create table
        updateTable();
    });
}

function updateTable() {
    //Create table with jquery
    let table = $("#instance-table");
    table.empty();
    console.log(instances);
    createHeader(table);
    createBody(table, filterInstances());
}

function createHeader(table) {
    let header = $("<thead>");
    header.addClass("thead-light");
    let row = $("<tr>");
    for (let key in instances[0]) {
        if (!FIELDS.includes(key)) {
            continue;
        }
        let cell = $("<th>");
        cell.attr("scope", "col");
        cell.text(key);
        row.append(cell);
    }
    header.append(row);
    table.append(header);
}

function createBody(table, items) {
    console.log(items);
    let body = $("<tbody>");
    for (let i = 0; i < items.length; i++) {
        let row = $("<tr>");
        for (let key in items[i]) {
            if (!FIELDS.includes(key)) {
                continue;
            }
            let cell = $("<td>");
            cell.text(items[i][key]);
            row.append(cell);
        }
        body.append(row);
    }
    table.append(body);
}

function filterInstances() {
    let ram_factor = selections.file_count * selections.users * selections.commits * selections.frequency
    let cpu_factor = selections.file_size * selections.file_count * selections.users * selections.commits * selections.frequency
    console.log(ram_factor, cpu_factor);

    let min_cpu = (Math.min((cpu_factor - 25) / 1500000, 1)) * 32;
    console.log(min_cpu)
    return instances.filter((instance) => {
        return (
            instance["vCPU"] >= min_cpu
            && instance["RAM (GB)"] >= .5
            && instance["CPU Max Clock (GHz)"] >= 3.1
        );
    });
}
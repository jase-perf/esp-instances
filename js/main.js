import { parse } from './vanillaes_csv/index.min.js'
var instances = [];
const FIELDS = ["Name", "vCPUs", "RAM (GB)", "CPU Speed", "Monthly Cost (on demand)", "Notes", "Cloud"]

var selections = {
    cloud: "all",
    min_vcpus: 0,
    min_ram: 0,
}

$().ready(() => {
    console.log("Ready!");
    initialSetup();
    $("select").on("change", function () {
        selections[this.id] = this.value;
        updateTable();
    });
});

function initialSetup() {
    $.get("data/all_instances.csv", (result) => {
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
    return instances.filter((instance) => {
        return (
            (instance["Cloud"] == selections["cloud"] || selections["cloud"] == "all")
            && instance["RAM (GB)"] >= selections["min_ram"]
            && instance["vCPUs"] >= selections["min_vcpus"]
        );
    });
}
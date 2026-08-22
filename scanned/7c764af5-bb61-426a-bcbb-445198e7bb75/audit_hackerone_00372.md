# [C] [query-mysql] SQL Injection due to lack of user input sanitization allows to run arbitrary SQL queries when fetching data from database

## Summary
Severity: Critical (CVSS 9.8)
Program: Node.js third-party modules
Weakness: SQL Injection
Reporter: bl4de
State: resolved
Disclosed: 2018-05-19T12:53:02.893Z
CVE: CVE-2018-3754
Source: https://hackerone.com/reports/311244

## Details
Hi Guys,

There is SQL Injection in query-mysql module. Due to lack of sanitization of user input, an attacker is able to craft SQL query and get any data from the database.

## Module

**query-mysql**

Install this module in your project like dependency

https://www.npmjs.com/package/query-mysql

version: 0.0.2

Stats
0 downloads in the last day
13 downloads in the last week
85 downloads in the last month

~1000 estimated downloads per year


## Description

Most of functions in ```query-mysql``` module used to manipulate data build query usign simple string concatenation. This leads to SQL Injection vulnerability, because an attacker is able to pass his own query and run any SQL on the database.

This is one of those functions, which allows to select record from the table depends on value for the column:

```javascript
// node_modules/query-mysql/lib/base.js, line 172
    fetchById: function (table, id, name_id, callback) {
        connect(function (connected) {
            if (connected) {

                connection.query("SELECT * FROM " + table + " WHERE " +name_id+"='"+ id+"'", function (err, rows, fields) {
                    connection.end();
                    console.log("fetchById");
                    //if (err) throw err;
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/311244_

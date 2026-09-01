# [H] [@azhou/basemodel] SQL injection

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: SQL Injection
Reporter: verichains
State: resolved
Disclosed: 2020-02-02T23:00:07.219Z
Source: https://hackerone.com/reports/506644

## Details
I would like to report SQL injection in @azhou/basemodel
It allows attacker to read data from database.

# Module

**module name:** @azhou/basemodel
**version:** 1.0.0
**npm page:** `https://www.npmjs.com/package/@azhou/basemodel`

## Module Description

### Usage

#### Initialization

```js
var model = require("@azhou/basemodel")(tableName, fields);
```
where `tableName` is the name of the data table and `fields` refers to the field list, either using comma connected string or array.

Example:
```js
// Initialize database
var db = require("@azhou/mysql-wrapper");
db.init("server", "database", "username", "password");

// Create basic CRUD data model
var model = require("@azhou/basemodel")("table", [ "field1", "field2", "field3", ... ]);
```

Notice when defining fields, `id` should not implicitly added and should not be contained in the field list

If validation is required, function `validate()` that returns boolean can be added to `model`:
```js
model.validate = function (source) { ... }
```

#### CRUD Functions

_Trimmed to 38 lines — full report: https://hackerone.com/reports/506644_

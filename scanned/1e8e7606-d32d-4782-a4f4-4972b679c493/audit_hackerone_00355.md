# [H] [egg-scripts] Command injection

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: pontus_johnson
State: resolved
Disclosed: 2018-08-19T07:27:08.095Z
CVE: CVE-2018-3786
Source: https://hackerone.com/reports/388936

## Details
I would like to report a command injection vulnerability in egg-scripts.
It allows arbitrary shell command execution through a maliciously crafted command line argument.

# Module

**module name:** [egg-scripts]
**version:** [2.6.0]
**npm page:** `https://www.npmjs.com/package/egg-scripts`

## Module Description

"deploy tool for egg project."

## Module Stats

Replace stats below with numbers from npm’s module page:

209 downloads in the last day
1,958 downloads in the last week
8,333 downloads in the last month

# Vulnerability

## Vulnerability Description

egg-script does not sanitize the --stderr command line argument, and subsequently passes it to child_process.exec(), thus allowing arbitrary shell command injection.

## Steps To Reproduce:

1. Install egg: `npm i egg --save`
2. Install egg-scripts: `sudo npm i egg-scripts -g --save`
3. Run eggctl with malicious argument: `eggctl start --daemon --stderr=/tmp/eggctl_stderr.log; touch /tmp/malicious`
4. Check that the injected command was executed: `ls /tmp/`
5. Stop eggctl: `eggctl stop`

## Patch

Command execution happens [here](https://github.com/eggjs/egg-scripts/blob/22faa4cfbb84cc5bc819d981dce962d8f95f8357/lib/cmd/start.js#L214):

_Trimmed to 38 lines — full report: https://hackerone.com/reports/388936_

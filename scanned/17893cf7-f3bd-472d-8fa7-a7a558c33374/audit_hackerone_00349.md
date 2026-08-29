# [C] [apex-publish-static-files] Command Injection on connectString

## Summary
Severity: Critical (CVSS 10.0)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: abdilahrf_
State: resolved
Disclosed: 2018-10-18T18:32:08.981Z
CVE: CVE-2018-16462
Source: https://hackerone.com/reports/405694

## Details
I would like to report a command injection vulnerability in the apex-publish-static-files npm module.
It allows arbitrary shell command execution through a maliciously crafted argument.

# Module

**module name:** apex-publish-static-files
**version:** 2.0.0
**npm page:** `https://www.npmjs.com/package/apex-publish-static-files`

## Module Description

>Uploads all files from a local directory to Oracle APEX

## Module Stats

15 downloads in the last day
~170 downloads in the last month

# Vulnerability

## Vulnerability Description

apex-publish-static-files does not sanitize the connectionString argument, and subsequently passes it to execSync(), thus allowing arbitrary shell command injection. 

Vulnerability Code : [https://github.com/vincentmorneau/apex-publish-static-files/blob/master/index.js#54-66](https://github.com/vincentmorneau/apex-publish-static-files/blob/master/index.js#54-66)

```
			const childProcess = execSync(
				'"' + opts.sqlclPath + '"' + // Sqlcl path
				' ' + opts.connectString + // Connect string (user/pass@server:port/sid)
				' @"' + path.resolve(__dirname, 'lib/script') + '"' + // Sql to execute
				' "' + path.resolve(__dirname, 'lib/distUpload.js') + '"' + // Param &1 (js to execute)
				' "' + path.resolve(opts.directory) + '"' + // Param &2
				' ' + opts.appID + // Param &3
				' "' + opts.destination + '"' + // Param &4
				' "' + opts.pluginName + '"' // Param &5
				, {
					encoding: 'utf8'
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/405694_

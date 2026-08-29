# [H] Arbitrary File Write Through Archive Extraction

## Summary
Severity: High (CVSS 8.2)
Program: Node.js third-party modules
Weakness: N/A
Reporter: danny_grander
State: resolved
Disclosed: 2018-08-12T14:46:51.027Z
CVE: CVE-2018-1002204
Source: https://hackerone.com/reports/362118

## Details
I would like to report arbitrary file write vulnerability in adm-zip module
It allows attackers to write arbitrary files when a malicious archive is extracted.
More info here: 
https://snyk.io/research/zip-slip-vulnerability
https://github.com/snyk/zip-slip-vulnerability#affected-libraries


# Module

**module name:** adm-zip
**version:** <0.4.9
**npm page:** `https://www.npmjs.com/package/adm-zip`

## Module Description
ADM-ZIP for NodeJS with added support for electron original-fs
ADM-ZIP is a pure JavaScript implementation for zip data compression for NodeJS.

## Module Stats

> Replace stats below with numbers from npm’s module page:

1.5M downloads in the last week

# Vulnerability

## Vulnerability Description
The vulnerability is a form of directory traversal that can be exploited by extracting files from an archive. The premise of the directory traversal vulnerability is that an attacker can gain access to parts of the file system outside of the target folder in which they should reside. The attacker can then overwrite executable files and either invoke them remotely or wait for the system or user to call them, thus achieving remote command execution on the victim’s machine. The vulnerability can also cause damage by overwriting configuration files or other sensitive resources, and can be exploited on both client (user) machines and servers.

The vulnerability is exploited using a specially crafted archive that holds directory traversal filenames (e.g.  ../../evil.sh). The Zip Slip vulnerability can affect numerous archive formats, including tar, jar, war,  cpio, apk, rar and 7z. If you’d like the information on this page in a downloadable technical white paper, click the button below.

More info here: 
https://snyk.io/research/zip-slip-vulnerability
https://github.com/snyk/zip-slip-vulnerability


## Steps To Reproduce:

Sample files can be found here: https://github.com/snyk/zip-slip-vulnerability/tree/master/archives

_Trimmed to 38 lines — full report: https://hackerone.com/reports/362118_

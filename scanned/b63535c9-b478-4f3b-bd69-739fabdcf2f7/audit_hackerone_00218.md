# [C] [cloudron-surfer] Denial of Service via LDAP Injection

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: LDAP Injection
Reporter: d3lla
State: resolved
Disclosed: 2020-08-22T08:48:44.185Z
Source: https://hackerone.com/reports/906959

## Details
I would like to report `Denial of service via LDAP Injection` vulnerability in `cloudron-surfer` module.
It allows a malicious attacker to send a malformed input that is interpreted as an LDAP filter, leading to Denial of Service.

# Module

**module name:** `cloudron-surfer`
**version:** `5.9.0`
**npm page:** `https://www.npmjs.com/package/cloudron-surfer`

## Module Description

Surfer is a Simple static file server. It comes with a commandline tool to upload files from your local folders and a webinterface to manage files directly on the server.

## Module Stats

[4] weekly downloads

# Vulnerability

## Vulnerability Description

The module is vulnerable to a DoS via LDAP Injection.
LDAP injection is a particular case of Injection vulnerabilities that occurs when user controlled input not properly sanitized is used to build LDAP filter. 
This could lead to modification of LDAP statements performed. Depending on the application, this could lead to an authentication bypass, information disclosure or DoS.

The problem arises during the login phase. User controlled input `username` is used to build a LDAP filter without any sanitization. 
The filter uses an `OR` operation between different attributes that are `uid`, `mail`, `username`, `sAMAccountName`.
The search returns all the users whose one of the attributes above has value `username`. Then it takes the first and match with the `password` provided using a `bind` operation.

The problem occurs when the `username` contains valid LDAP character filters, like for example `*` (the filter `(cn=*)` is a presence filter that will match any entry with one or more values for the `cn` attribute), that could change the LDAP statement.

If an attacker provides as `username` the value `*`, this will result in the following filter:
`(|(uid=*)(mail=*)(username=*)(sAMAccountName=*))`.

In order for an attacker to perform a DoS, he/she has to build a filter that will take long time to be evaluated.
For example, if the attacker provides the following payload `*)(cn=*)(cn=*`, this will result in the following filter:
`(|(uid=*)(cn=*)(cn=*)(mail=*)(cn=*)(cn=*)(username=*)(cn=*)(cn=*)(sAMAccountName=*)(cn=*)(cn=*))`.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/906959_

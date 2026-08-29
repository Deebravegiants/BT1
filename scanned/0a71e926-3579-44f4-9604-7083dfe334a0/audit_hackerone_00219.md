# [C] [meemo-app] Denial of Service via LDAP Injection

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: LDAP Injection
Reporter: d3lla
State: resolved
Disclosed: 2020-08-22T08:48:33.856Z
Source: https://hackerone.com/reports/907311

## Details
I would like to report `Denial of service via LDAP Injection` vulnerability in `meemo-app` module.
It allows a malicious attacker to send a crafted input that is interpreted as an LDAP filter, leading to Denial of Service.

# Module

**module name:** `meemo-app`
**version:** `1.9.2`
**npm page:** `https://www.npmjs.com/package/meemo-app`

## Module Description

Meemo is a personal data manager. It lets you simply input any kind of information like notes, thoughts, ideas as well as acts as a bookmarkmanager and todo list. The user interface resembles a news feed organized with tags. Full text search further allows you to quickly find information in your pile of accumulated data.

For better bookmarking, there are chrome and firefox webextensions available.

## Module Stats

[1] weekly downloads

# Vulnerability

## Vulnerability Description

The module is vulnerable to a DoS via LDAP Injection.
The causes of this vulnerability are the same of another report here #906959.


Below the vulnerable code:

```javascript
...
function verify(username, password, callback) {
    profile(username, true, function (error, result) {
        if (error) return callback(error);

        if (process.env.CLOUDRON_LDAP_URL) {
            var ldapClient = ldapjs.createClient({ url: process.env.CLOUDRON_LDAP_URL });
            ldapClient.on('error', function (error) {
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/907311_

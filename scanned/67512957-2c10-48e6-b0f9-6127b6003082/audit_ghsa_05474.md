# [C] Apache Continuum vulnerable to Command Injection through Installations REST API

## Summary
Severity: Critical
Advisory: GHSA-77p9-w6pj-rmvg
CVE: CVE-2016-15057
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-77p9-w6pj-rmvg
Type: github-advisory

## Affected
- Maven: `org.apache.continuum:continuum` — affected >=0

## Details
***UNSUPPORTED WHEN ASSIGNED*** 

Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in Apache Continuum.

This issue affects Apache Continuum: all versions.

Attackers with access to the Installations REST API can use this to invoke arbitrary commands on the server.

As this project is retired, we do not plan to release a version that fixes this issue. Users are recommended to find an alternative or restrict access to the instance to trusted users.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15057
- https://github.com/apache/continuum
- https://lists.apache.org/thread/hbvf1ztqw2kv51khvzm5nk3mml3nm4z1
- http://www.openwall.com/lists/oss-security/2026/01/26/1

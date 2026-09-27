# [C] CVE-2018-1309

## Summary
Severity: Critical
Advisory: CVE-2018-1309
Aliases: GHSA-42wx-65g4-5cxv
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-1309
Type: osv

## Details
Apache NiFi External XML Entity issue in SplitXML processor. Malicious XML content could cause information disclosure or remote code execution. The fix to disable external general entity parsing and disallow doctype declarations was applied on the Apache NiFi 1.6.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nifi.apache.org/security.html#CVE-2018-1309

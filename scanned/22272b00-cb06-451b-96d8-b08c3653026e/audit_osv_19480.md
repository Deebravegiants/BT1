# [C] CVE-2021-21386

## Summary
Severity: Critical
Advisory: CVE-2021-21386
Aliases: GHSA-8434-v7xw-8m9x, PYSEC-2026-281
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-24
Source: https://osv.dev/vulnerability/CVE-2021-21386
Type: osv

## Details
APKLeaks is an open-source project for scanning APK file for URIs, endpoints & secrets. APKLeaks prior to v2.0.3 allows remote attackers to execute arbitrary OS commands via package name inside application manifest. An attacker could include arguments that allow unintended commands or code to be executed, allow sensitive data to be read or modified or could cause other unintended behavior through malicious package name. The problem is fixed in version v2.0.6-dev and above.

## References
- https://github.com/dwisiswant0/apkleaks/commit/a966e781499ff6fd4eea66876d7532301b13a382
- https://github.com/dwisiswant0/apkleaks/security/advisories/GHSA-8434-v7xw-8m9x

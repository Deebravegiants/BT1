# [H] ezsystems/ezpublish-legacy has a SQL injection in dfscleanup

## Summary
Severity: High
Advisory: GHSA-xg9x-h37w-h3r3
CVE: CVE-2026-38739
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-xg9x-h37w-h3r3
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected 2019.03

## Details
NB: All tags and branches in this repository are past their end of life, so the vulnerability will not be fixed. The advisory is posted on the request of the researcher, for the information of anyone who might still use this software.

### Impact
There is a security vulnerability in eZ Publish Legacy, affecting the dfscleanup.php script and the `_getFileList` function of the `eZDFSFileHandlerMySQLiBackend` class (kernel/private/classes/clusterfilehandlers/dfsbackends/mysqli.php). The vulnerability allows an attacker with local shell access and sufficient privileges to run dfscleanup.php to perform a union-based SQL injection against the eZ Publish MySQL database, potentially exposing sensitive data such as user credentials.

It is known to affect the branch 2019.03, and it may well affect other branches.

### Credit
The issue was found and reported by security auditor Timothé Ridel from Advens:
https://www.advens.com/

### Patches
None, the software is past its end of life.

### Workarounds
None.

### Resources
- Report by Advens: https://github.com/Goaterino/ezpublish-legacy-lab/blob/main/SQL%20injection%20and%20arbitrary%20file%20deletion%20in%20dfscleanup.md

## References
- https://github.com/ezsystems/ezpublish-legacy/security/advisories/GHSA-xg9x-h37w-h3r3
- https://github.com/ezsystems/ezpublish-legacy

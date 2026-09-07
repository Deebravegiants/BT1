# [C] SQL Injection in liftkit/database

## Summary
Severity: Critical
Advisory: GHSA-8hcf-2m4v-f2rq
CVE: CVE-2016-15020
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-16
Source: https://github.com/advisories/GHSA-8hcf-2m4v-f2rq
Type: github-advisory

## Affected
- Packagist: `liftkit/database` — affected >=0 <2.13.2

## Details
A vulnerability was found in liftkit database up to 2.13.1. It has been classified as critical. This affects the function processOrderBy of the file src/Query/Query.php. The manipulation leads to sql injection. Upgrading to version 2.13.2 is able to address this issue. The name of the patch is 42ec8f2b22e0b0b98fb5b4444ed451c1b21d125a. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-218391.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15020
- https://github.com/liftkit/database/commit/42ec8f2b22e0b0b98fb5b4444ed451c1b21d125a
- https://github.com/liftkit/database
- https://github.com/liftkit/database/releases/tag/v2.13.2
- https://vuldb.com/?ctiid.218391
- https://vuldb.com/?id.218391

# [H] Code injection in dolibarr/dolibarr

## Summary
Severity: High
Advisory: GHSA-42qm-c3cf-9wv2
CVE: CVE-2022-0819
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-03
Source: https://github.com/advisories/GHSA-42qm-c3cf-9wv2
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <15.0.1

## Details
Improper php function sanitization, lead to an ability to inject arbitrary PHP code and run arbitrary commands on file system. In the function "dol_eval" in file "dolibarr/htdocs/core/lib/functions.lib.php" dangerous PHP functions are sanitized using "str_replace" and can be bypassed using following code in $s parameter

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0819
- https://github.com/dolibarr/dolibarr/commit/2a48dd349e7de0d4a38e448b0d2ecbe25e968075
- https://github.com/dolibarr/dolibarr
- https://huntr.dev/bounties/b03d4415-d4f9-48c8-9ae2-d3aa248027b5

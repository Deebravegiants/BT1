# [M] snipe-it is vulnerable to Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-9vwf-54m9-gc4f
CVE: CVE-2021-4089
CWE: CWE-284, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-9vwf-54m9-gc4f
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <5.3.4

## Details
snipe-it prior to version 5.3.4 is vulnerable to Improper Access Control. Regular users with `DENY` set to all models permissions can still view model information via the /models/{id}/clone endpoint due to no authorize('view') permission being set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4089
- https://github.com/snipe/snipe-it/commit/1699c09758e56f740437674a8d6ba36443399f24
- https://github.com/snipe/snipe-it
- https://huntr.dev/bounties/19453ef1-4d77-4cff-b7e8-1bc8f3af0862

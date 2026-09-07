# [H] Cross-Site Request Forgery vulnerability in Prefect

## Summary
Severity: High
Advisory: GHSA-4hh5-2678-83fx
CVE: CVE-2023-6022
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-4hh5-2678-83fx
Type: github-advisory

## Affected
- PyPI: `prefect` — affected >=2.0.0 <2.16.5

## Details
An attacker is able to steal secrets and potentially gain remote code execution via CSRF using a self-hosted, open source Prefect API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6022
- https://github.com/prefecthq/prefect/commit/227dfcc7e3374c212a4bcd68b14e090b1c02d9d3
- https://github.com/PrefectHQ/prefect/blob/main/RELEASE-NOTES.md#release-2165
- https://github.com/prefecthq/prefect
- https://huntr.com/bounties/dab47d99-551c-4355-9ab1-c99cb90235af

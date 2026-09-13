# [M] Snipe-IT vulnerable to Improper Authentication

## Summary
Severity: Medium
Advisory: GHSA-fhvv-p968-6vvj
CVE: CVE-2022-3173
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-18
Source: https://github.com/advisories/GHSA-fhvv-p968-6vvj
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <6.0.10

## Details
Snipe-IT prior to 6.0.10 is vulnerable to Improper Authentication. A user without the `View and Modify License Files` permission may access files uploaded to licenses as long as they have the `View` permission for licenses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3173
- https://github.com/snipe/snipe-it/commit/dcab1381e7ee0b7fd1df3a34750dbff4b79185b2
- https://github.com/snipe/snipe-it
- https://huntr.dev/bounties/6d8ffcc6-c6e3-4385-8ead-bdbbbacf79e9

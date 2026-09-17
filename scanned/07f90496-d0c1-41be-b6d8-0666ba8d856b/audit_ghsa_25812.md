# [C] OS Command Injection in GenieACS

## Summary
Severity: Critical
Advisory: GHSA-2877-693q-pj33
CVE: CVE-2021-46704
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-07
Source: https://github.com/advisories/GHSA-2877-693q-pj33
Type: github-advisory

## Affected
- npm: `genieacs` — affected >=0 <1.2.8

## Details
In GenieACS 1.2.x before 1.2.8, the UI interface API is vulnerable to unauthenticated OS command injection via the ping host argument (lib/ui/api.ts and lib/ping.ts). The vulnerability arises from insufficient input validation combined with a missing authorization check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46704
- https://github.com/genieacs/genieacs/commit/7f295beeecc1c1f14308a93c82413bb334045af6
- https://github.com/genieacs/genieacs
- https://github.com/genieacs/genieacs/releases/tag/v1.2.8

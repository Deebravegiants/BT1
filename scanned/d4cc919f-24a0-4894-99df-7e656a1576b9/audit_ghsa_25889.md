# [M] Path traversal in FreeTAKServer-UI

## Summary
Severity: Medium
Advisory: GHSA-7cr9-rmqr-fpqp
CVE: CVE-2022-25511
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-7cr9-rmqr-fpqp
Type: github-advisory

## Affected
- PyPI: `FreeTAKServer-UI` — affected >=0

## Details
An issue in the ?filename= argument of the route /DataPackageTable in FreeTAKServer-UI v1.9.8 allows attackers to place arbitrary files anywhere on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25511
- https://github.com/FreeTAKTeam/UI/issues/29
- https://github.com/FreeTAKTeam/UI

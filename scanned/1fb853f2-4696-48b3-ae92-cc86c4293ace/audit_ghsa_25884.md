# [M] Cross-site Scripting in FreeTAKServer-UI

## Summary
Severity: Medium
Advisory: GHSA-gjh6-wvhq-h4qx
CVE: CVE-2022-25507
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-gjh6-wvhq-h4qx
Type: github-advisory

## Affected
- PyPI: `FreeTAKServer-UI` — affected >=0

## Details
FreeTAKServer-UI v1.9.8 was discovered to contain a stored cross-site scripting (XSS) vulnerability via the Callsign parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25507
- https://github.com/FreeTAKTeam/UI/issues/28
- https://github.com/FreeTAKTeam/UI

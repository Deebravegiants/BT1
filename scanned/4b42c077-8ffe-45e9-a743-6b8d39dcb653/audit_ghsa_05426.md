# [M] records-mover Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p3jp-7gj7-h6pr
CVE: CVE-2023-7333
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-p3jp-7gj7-h6pr
Type: github-advisory

## Affected
- PyPI: `records-mover` — affected >=0 <1.6.0

## Details
A weakness has been identified in bluelabsio records-mover up to 1.5.4. The affected element is an unknown function of the component Table Object Handler. This manipulation causes SQL Injection. The attack needs to be launched locally. Upgrading to version 1.6.0 is sufficient to fix this issue. Patch name: 3f8383aa89f45d861ca081e3e9fd2cc9d0b5dfaa. Developers should upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-7333
- https://github.com/bluelabsio/records-mover/pull/254
- https://github.com/bluelabsio/records-mover/commit/3f8383aa89f45d861ca081e3e9fd2cc9d0b5dfaa
- https://github.com/bluelabsio/records-mover
- https://github.com/bluelabsio/records-mover/releases/tag/v1.6.0
- https://vuldb.com/?ctiid.339566
- https://vuldb.com/?id.339566

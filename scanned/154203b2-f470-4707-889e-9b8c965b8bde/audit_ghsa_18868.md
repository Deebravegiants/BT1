# [M] Taguette vulnerable to cross-site scripting via tag name, tag description, document name and document description

## Summary
Severity: Medium
Advisory: GHSA-g9qw-g6rv-3889
CVE: CVE-2025-62528
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-g9qw-g6rv-3889
Type: github-advisory

## Affected
- PyPI: `taguette` — affected >=0 <1.5.0

## Details
### Impact
An issue has been discovered in Taguette versions prior to 1.5.0. It was possible for a project member to put JavaScript in name or description fields which would run on project load.

### Patches
Users should upgrade to Taguette 1.5.0.

### References
- https://gitlab.com/remram44/taguette/-/issues/330

## References
- https://github.com/remram44/taguette/security/advisories/GHSA-g9qw-g6rv-3889
- https://nvd.nist.gov/vuln/detail/CVE-2025-62528
- https://github.com/pypa/advisory-database/tree/main/vulns/taguette/PYSEC-2025-188.yaml
- https://github.com/remram44/taguette
- https://gitlab.com/remram44/taguette/-/issues/330

# [M] pytest has vulnerable tmpdir handling

## Summary
Severity: Medium
Advisory: GHSA-6w46-j5rx-g56g
CVE: CVE-2025-71176
CWE: CWE-379
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-6w46-j5rx-g56g
Type: github-advisory

## Affected
- PyPI: `pytest` — affected >=0 <9.0.3

## Details
pytest through 9.0.2 on UNIX relies on directories with the `/tmp/pytest-of-{user}` name pattern, which allows local users to cause a denial of service or possibly gain privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-71176
- https://github.com/pytest-dev/pytest/issues/13669
- https://github.com/pytest-dev/pytest/pull/14343
- https://github.com/pytest-dev/pytest/commit/95d8423bd24992deea5b9df32555fa1741679e2c
- https://github.com/pytest-dev/pytes
- https://github.com/pytest-dev/pytest/releases/tag/9.0.3
- https://www.openwall.com/lists/oss-security/2026/01/21/5

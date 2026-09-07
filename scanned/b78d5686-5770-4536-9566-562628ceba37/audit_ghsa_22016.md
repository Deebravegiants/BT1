# [M] Bodhi Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h896-6hcp-gj6c
CVE: CVE-2017-1002152
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h896-6hcp-gj6c
Type: github-advisory

## Affected
- PyPI: `bodhi` — affected >=0 <2.9.1

## Details
Bodhi 2.9.0 and lower is vulnerable to cross-site scripting resulting in code injection caused by incorrect validation of bug titles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1002152
- https://github.com/fedora-infra/bodhi/issues/1740
- https://github.com/fedora-infra/bodhi/commit/2a3b06b42242ecabb7fed6b147b033b36292d76f
- https://bugzilla.redhat.com/show_bug.cgi?id=1478587
- https://github.com/fedora-infra/bodhi
- https://github.com/pypa/advisory-database/tree/main/vulns/bodhi/PYSEC-2019-150.yaml

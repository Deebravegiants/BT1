# [M]  pip: Path traversal in console_scripts/gui_scripts entry point names allows installing scripts outside of target directory

## Summary
Severity: Medium
Advisory: GHSA-wf93-45jw-7689
CVE: CVE-2026-8643
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-wf93-45jw-7689
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <26.1.2

## Details
pip would treat console_scripts and gui_scripts as paths instead of file names without sanitizing the resolved absolute path to the installation directory, leading to entry points being installed outside the installation directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8643
- https://github.com/pypa/pip/pull/14000
- https://access.redhat.com/errata/RHSA-2026:33313
- https://access.redhat.com/errata/RHSA-2026:34776
- https://access.redhat.com/errata/RHSA-2026:34777
- https://access.redhat.com/errata/RHSA-2026:34778
- https://access.redhat.com/errata/RHSA-2026:34780
- https://access.redhat.com/errata/RHSA-2026:34891
- https://access.redhat.com/errata/RHSA-2026:36193
- https://access.redhat.com/errata/RHSA-2026:36315
- https://access.redhat.com/errata/RHSA-2026:37275
- https://access.redhat.com/errata/RHSA-2026:37283
- https://access.redhat.com/security/cve/CVE-2026-8643
- https://bugzilla.redhat.com/show_bug.cgi?id=2460927
- https://github.com/pypa/advisory-database/tree/main/vulns/pip/PYSEC-2026-196.yaml
- https://github.com/pypa/pip
- https://mail.python.org/archives/list/security-announce@python.org/thread/YV63UET5D3OOJY7O4M5XCVYO2YM4NBYJ
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-8643.json
- https://access.redhat.com/errata/RHSA-2026:34374
- https://access.redhat.com/errata/RHSA-2026:34456

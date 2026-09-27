# [M] awxkit has a path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g29c-rgq6-gxgj
CVE: CVE-2026-52902
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-g29c-rgq6-gxgj
Type: github-advisory

## Affected
- PyPI: `awxkit` — affected >=0

## Details
A path traversal vulnerability was found in awxkit, the CLI tool for AWX. The YAML !include directive does not sanitize file paths, allowing an attacker to craft a malicious YAML file that reads arbitrary YAML-formatted files from the local filesystem when a user imports it using "awx --conf.format yaml import". This is a client-side vulnerability requiring user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-52902
- https://access.redhat.com/security/cve/CVE-2026-52902
- https://bugzilla.redhat.com/show_bug.cgi?id=2486729
- https://github.com/ansible/awx

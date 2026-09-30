# [M] Path Traversal in Ansible

## Summary
Severity: Medium
Advisory: GHSA-3c67-gc48-983w
CVE: CVE-2020-10691
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-3c67-gc48-983w
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.7

## Details
An archive traversal flaw was found in all ansible-engine versions 2.9.x prior to 2.9.7, when running `ansible-galaxy collection` install. When extracting a collection .tar.gz file, the directory is created without sanitizing the filename. An attacker could take advantage to overwrite any file within the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10691
- https://github.com/ansible/ansible/pull/68596
- https://github.com/ansible/ansible/commit/b2551bb6943eec078066aa3a923e0bb3ed85abe8
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10691
- https://github.com/advisories/GHSA-3c67-gc48-983w
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-2.yaml

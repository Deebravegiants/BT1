# [M] Ansible galaxy-importer Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-55g2-vm3q-7w52
CVE: CVE-2023-5189
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-55g2-vm3q-7w52
Type: github-advisory

## Affected
- PyPI: `galaxy-importer` — affected >=0

## Details
A path traversal vulnerability exists in Ansible when extracting tarballs. An attacker could craft a malicious tarball so that when using the galaxy importer of Ansible Automation Hub, a symlink could be dropped on the disk, resulting in files being overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5189
- https://access.redhat.com/errata/RHSA-2023:7773
- https://access.redhat.com/errata/RHSA-2024:1536
- https://access.redhat.com/errata/RHSA-2024:2010
- https://access.redhat.com/security/cve/CVE-2023-5189
- https://bugzilla.redhat.com/show_bug.cgi?id=2234387
- https://github.com/ansible/galaxy-importer
- https://github.com/ansible/galaxy-importer/blob/2c5c7c05fdfb0835878234b36de32902c703616d/galaxy_importer/collection.py#L160-L165

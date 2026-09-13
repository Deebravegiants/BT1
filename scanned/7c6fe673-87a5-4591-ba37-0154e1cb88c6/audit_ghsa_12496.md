# [M] Ansible symlink attack vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jpvw-p8pr-9g2x
CVE: CVE-2023-5115
CWE: CWE-22, CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-12-28
Source: https://github.com/advisories/GHSA-jpvw-p8pr-9g2x
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <8.5.0

## Details
An absolute path traversal attack exists in the Ansible automation platform. This flaw allows an attacker to craft a malicious Ansible role and make the victim execute the role. A symlink can be used to overwrite a file outside of the extraction path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5115
- https://github.com/ansible/ansible/commit/1e930684bc0a76ec3d094cd326738ad26416541c
- https://access.redhat.com/errata/RHSA-2023:5701
- https://access.redhat.com/errata/RHSA-2023:5758
- https://access.redhat.com/security/cve/CVE-2023-5115
- https://bugzilla.redhat.com/show_bug.cgi?id=2233810
- https://github.com/ansible-community/ansible-build-data/blob/16d36538b96c65d9e0e28d89781361b69857ac0e/8/CHANGELOG-v8.rst#L221
- https://github.com/ansible/ansible
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html

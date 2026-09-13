# [M] ansible-core Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-32p4-gm2c-wmch
CVE: CVE-2024-9902
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-32p4-gm2c-wmch
Type: github-advisory

## Affected
- PyPI: `ansible-core` — affected >=0 <2.14.18rc1
- PyPI: `ansible-core` — affected >=2.15.0b1 <2.15.13rc1
- PyPI: `ansible-core` — affected >=2.16.0b1 <2.16.13rc1
- PyPI: `ansible-core` — affected >=2.17.0b1 <2.17.6rc1
- PyPI: `ansible-core` — affected >=2.18.0b1 <2.18.0rc2

## Details
A flaw was found in Ansible. The ansible-core `user` module can allow an unprivileged user to silently create or replace the contents of any file on any system path and take ownership of it when a privileged user executes the `user` module against the unprivileged user's home directory. If the unprivileged user has traversal permissions on the directory containing the exploited target file, they retain full control over the contents of the file as its owner.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9902
- https://github.com/ansible/ansible/commit/03794735d370db98a5ec2ad514fab2b0dd22d6be
- https://github.com/ansible/ansible/commit/03daf774d0d80fb7235910ed1c2b4fbcaebdfe65
- https://github.com/ansible/ansible/commit/3b6de811abea0a811e03e3029222a7e459922892
- https://github.com/ansible/ansible/commit/9d7312f695639e804d2caeb1d0f51c716a9ac7dd
- https://github.com/ansible/ansible/commit/f7be90626da3035c697623dcf9c90b7a0bc91c92
- https://access.redhat.com/errata/RHSA-2024:10762
- https://access.redhat.com/errata/RHSA-2024:8969
- https://access.redhat.com/errata/RHSA-2024:9894
- https://access.redhat.com/errata/RHSA-2025:1861
- https://access.redhat.com/security/cve/CVE-2024-9902
- https://bugzilla.redhat.com/show_bug.cgi?id=2318271
- https://github.com/ansible/ansible
- https://lists.debian.org/debian-lts-announce/2024/11/msg00021.html

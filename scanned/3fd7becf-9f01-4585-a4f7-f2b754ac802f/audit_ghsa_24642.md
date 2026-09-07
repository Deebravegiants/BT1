# [H] Ansible Exposes Sensitive Information

## Summary
Severity: High
Advisory: GHSA-5rrg-rr89-x9mv
CVE: CVE-2021-20228
CWE: CWE-200, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-5rrg-rr89-x9mv
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.10.0a1 <2.10.6rc1
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.18rc1
- PyPI: `ansible` — affected >=0 <2.8.19rc1

## Details
A flaw was found in the Ansible Engine prior to 2.10.6rc1, 2.9.18rc1, and 2.8.19rc1, where sensitive info is not masked by default and is not protected by the `no_log` feature when using the sub-option feature of the basic.py module. This flaw allows an attacker to obtain sensitive information. The highest threat from this vulnerability is to confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20228
- https://github.com/ansible/ansible/pull/73487
- https://github.com/ansible/ansible/pull/73492
- https://github.com/ansible/ansible/pull/73493
- https://github.com/ansible/ansible/pull/73494
- https://github.com/ansible/ansible/commit/49ebd509df9de1c1fc1bcee00e79a835dd00662c
- https://github.com/ansible/ansible/commit/e41d1f0a3fd6c466192e7e24accd3d1c6501111b
- https://github.com/ansible/ansible/commit/f8ff395d817c3eddc050f809919c15dfb5796120
- https://bugzilla.redhat.com/show_bug.cgi?id=1925002
- https://github.com/advisories/GHSA-5rrg-rr89-x9mv
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2021-1.yaml
- https://www.debian.org/security/2021/dsa-4950

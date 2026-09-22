# [M] Path Traversal in Ansible

## Summary
Severity: Medium
Advisory: GHSA-gfr2-qpxh-qj9m
CVE: CVE-2020-1735
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-gfr2-qpxh-qj9m
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.18
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.12
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.8

## Details
A flaw was found in the Ansible Engine when the fetch module is used. An attacker could intercept the module, inject a new path, and then choose a new destination path on the controller node. All versions in 2.7.x, 2.8.x and 2.9.x branches are believed to be vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1735
- https://github.com/ansible/ansible/issues/67793
- https://github.com/ansible/ansible/pull/69023
- https://github.com/ansible/ansible/pull/69024
- https://github.com/ansible/ansible/pull/69025
- https://github.com/ansible/ansible/commit/18f91bbb88a84b1d3614ef41c3550da735592ac1
- https://github.com/ansible/ansible/commit/40969ff43812fabf5397f818d9e521f9b39c9c9a
- https://github.com/ansible/ansible/commit/de9a4f5474c5f5db442ae7493d6b5da7177e335d
- https://security.gentoo.org/glsa/202006-11
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WQVOQD4VAIXXTVQAJKTN7NUGTJFE2PCB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MRRYUU5ZBLPBXCYG6CFP35D64NP2UB2S
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DKPA4KC3OJSUFASUYMG66HKJE7ADNGFW
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-7.yaml
- https://github.com/ansible/ansible/blob/stable-2.9/changelogs/CHANGELOG-v2.9.rst#security-fixes-7
- https://github.com/ansible/ansible
- https://github.com/advisories/GHSA-gfr2-qpxh-qj9m
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1735

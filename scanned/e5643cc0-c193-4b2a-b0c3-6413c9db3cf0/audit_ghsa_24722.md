# [H] Ansible Uses Plugins That Disclose Credentials

## Summary
Severity: High
Advisory: GHSA-pm48-cvv2-29q5
CVE: CVE-2019-14846
CWE: CWE-117, CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pm48-cvv2-29q5
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.6.20
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.14
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.6

## Details
Ansible, all ansible_engine-2.x versions and ansible_engine-3.x up to ansible_engine-3.5, was logging at the DEBUG level which lead to a disclosure of credentials if a plugin used a library that logged credentials at the DEBUG level. This flaw does not affect Ansible modules, as those are executed in a separate process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14846
- https://github.com/ansible/ansible/pull/63366
- https://github.com/ansible/ansible/commit/90e74dd2600e5cc42dd9b4f4656f3d651c4ce5c4
- https://github.com/ansible/ansible/commit/cb0f535a8b254a2daf69cd067e842fabb2993034
- https://github.com/ansible/ansible/commit/d961f676c01023a6a21503df16ba551a550e515b
- https://access.redhat.com/errata/RHSA-2019:3201
- https://access.redhat.com/errata/RHSA-2019:3202
- https://access.redhat.com/errata/RHSA-2019:3203
- https://access.redhat.com/errata/RHSA-2019:3207
- https://access.redhat.com/errata/RHSA-2020:0756
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14846
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2019-4.yaml
- https://lists.debian.org/debian-lts-announce/2020/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00023.html
- https://www.debian.org/security/2021/dsa-4950
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00026.html

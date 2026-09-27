# [H] Ansible Leaks Data Passed to ssh-keygen

## Summary
Severity: High
Advisory: GHSA-hwrm-63v2-42g4
CVE: CVE-2018-16837
CWE: CWE-311
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hwrm-63v2-42g4
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.1
- PyPI: `ansible` — affected >=2.6.0a1 <2.6.7
- PyPI: `ansible` — affected >=0 <2.5.11

## Details
Ansible "User" module leaks any data which is passed on as a parameter to ssh-keygen. This could lean in undesirable situations such as passphrases credentials passed as a parameter for the ssh-keygen executable. Showing those credentials in clear text form for every user which have access just to the process list.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16837
- https://github.com/ansible/ansible/pull/47487
- https://github.com/ansible/ansible/pull/47486
- https://github.com/ansible/ansible/pull/47445
- https://github.com/ansible/ansible/pull/47436
- https://github.com/ansible/ansible/commit/77928e6c3a2ad878b20312ce5d74d9d7741e0df0
- https://github.com/ansible/ansible/commit/b618339c321c387230d3ea523e80ad47af3de5cf
- https://github.com/ansible/ansible/commit/f50cc0b8cb399bb7b7c1ad23b94c9404f0cc6d23
- https://www.debian.org/security/2019/dsa-4396
- https://web.archive.org/web/20200227105539/http://www.securityfocus.com/bid/105700
- https://usn.ubuntu.com/4072-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00012.html
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-44.yaml
- https://github.com/ansible/ansible/blob/c963ef1dfbf73efea5106624eb48b346f01eaefd/changelogs/CHANGELOG-v2.7.rst?plain=1#L138
- https://github.com/ansible/ansible
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16837
- https://access.redhat.com/security/cve/cve-2018-16837
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2018:3463
- https://access.redhat.com/errata/RHSA-2018:3462

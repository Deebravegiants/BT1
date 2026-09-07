# [M] Mercurial Path Traversal/Link Following vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mq66-vcfc-8246
CVE: CVE-2019-3902
CWE: CWE-22, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-mq66-vcfc-8246
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.9

## Details
A flaw was found in Mercurial before 4.9. It was possible to use symlinks and subrepositories to defeat Mercurial's path-checking logic and write files outside a repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3902
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3902
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2019-188.yaml
- https://lists.debian.org/debian-lts-announce/2019/04/msg00024.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00032.html
- https://usn.ubuntu.com/4086-1
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.9_.282019-02-01.29

# [H] Mercurial has Incorrect Permission Assignment for Critical Resource

## Summary
Severity: High
Advisory: GHSA-ghjx-3jg5-h6r2
CVE: CVE-2017-9462
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-ghjx-3jg5-h6r2
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.1.3

## Details
In Mercurial before 4.1.3, "hg serve --stdio" allows remote authenticated users to launch the Python debugger, and consequently execute arbitrary code, by using --debugger as a repository name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9462
- https://access.redhat.com/errata/RHSA-2017:1576
- https://bugs.debian.org/861243
- https://github.com/advisories/GHSA-ghjx-3jg5-h6r2
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2017-91.yaml
- https://lists.debian.org/debian-lts-announce/2018/07/msg00005.html
- https://security.gentoo.org/glsa/201709-18
- https://web.archive.org/web/20200227162318/http://www.securityfocus.com/bid/99123
- https://www.mercurial-scm.org/repo/hg/rev/77eaf9539499
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.1.3_.282017-4-18.29
- http://www.debian.org/security/2017/dsa-3963

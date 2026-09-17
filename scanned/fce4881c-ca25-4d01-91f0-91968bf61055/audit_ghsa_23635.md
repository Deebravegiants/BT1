# [C] Mercurial vulnerable to arbitrary code injection

## Summary
Severity: Critical
Advisory: GHSA-6v56-cpg6-3rpx
CVE: CVE-2017-17458
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6v56-cpg6-3rpx
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.4.1

## Details
In Mercurial before 4.4.1, it is possible that a specially malformed repository can cause Git subrepositories to run arbitrary code in the form of a `.git/hooks/post-update` script checked into the repository. Typical use of Mercurial prevents construction of such repositories, but they can be created programmatically.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17458
- https://bz.mercurial-scm.org/show_bug.cgi?id=5730
- https://confluence.atlassian.com/sourcetreekb/sourcetree-security-advisory-2018-01-24-942834324.html
- https://github.com/dscho/hg
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2017-90.yaml
- https://lists.debian.org/debian-lts-announce/2017/12/msg00027.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00005.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00041.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00032.html
- https://web.archive.org/web/20200227132808/http://www.securityfocus.com/bid/102926
- https://www.mercurial-scm.org/pipermail/mercurial-devel/2017-November/107333.html
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.4.1_.282017-11-07.29

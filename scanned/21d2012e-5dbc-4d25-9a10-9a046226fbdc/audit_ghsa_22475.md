# [H] Mercurial vulnerable to arbitrary code execution when converting Git repos

## Summary
Severity: High
Advisory: GHSA-49cw-434h-qc57
CVE: CVE-2016-3105
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-49cw-434h-qc57
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <3.8

## Details
The convert extension in Mercurial before 3.8 might allow context-dependent attackers to execute arbitrary code via a crafted git repository name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3105
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2016-28.yaml
- https://security.gentoo.org/glsa/201612-19
- https://selenic.com/hg/rev/a56296f55a5e
- https://web.archive.org/web/20200228012056/http://www.securityfocus.com/bid/90536
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_3.8_.2F_3.8.1_.282016-5-1.29
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00082.html
- http://www.debian.org/security/2016/dsa-3570
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.533255

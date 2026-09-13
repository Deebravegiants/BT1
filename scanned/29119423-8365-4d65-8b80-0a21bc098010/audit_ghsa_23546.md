# [H] Mercurial arbitrary code execution via a crafted git ext:: URL 

## Summary
Severity: High
Advisory: GHSA-j7c2-rqm3-c97m
CVE: CVE-2016-3068
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j7c2-rqm3-c97m
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <3.7.3

## Details
Mercurial before 3.7.3 allows remote attackers to execute arbitrary code via a crafted git ext:: URL when cloning a subrepository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3068
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2016-26.yaml
- https://security.gentoo.org/glsa/201612-19
- https://selenic.com/repo/hg-stable/rev/34d43cb85de8
- https://web.archive.org/web/20200228003737/http://www.securityfocus.com/bid/85733
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_3.7.3_.282016-3-29.29
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181505.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181542.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00043.html
- http://rhn.redhat.com/errata/RHSA-2016-0706.html
- http://www.debian.org/security/2016/dsa-3542
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html

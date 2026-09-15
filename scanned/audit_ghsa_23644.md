# [H] Mercurial arbitrary code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-9vjf-jjcq-3gh7
CVE: CVE-2016-3630
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9vjf-jjcq-3gh7
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <3.7.3

## Details
The binary delta decoder in Mercurial before 3.7.3 allows remote attackers to execute arbitrary code via a (1) clone, (2) push, or (3) pull command, related to (a) a list sizing rounding error and (b) short records.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3630
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2016-29.yaml
- https://security.gentoo.org/glsa/201612-19
- https://selenic.com/repo/hg-stable/rev/b6ed2505d6cf
- https://selenic.com/repo/hg-stable/rev/b9714d958e89
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_3.7.3_.282016-3-29.29
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181505.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181542.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00043.html
- http://www.debian.org/security/2016/dsa-3542
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html

# [H] Mercurial missing symlink check

## Summary
Severity: High
Advisory: GHSA-hvr9-wr9p-grgr
CVE: CVE-2017-1000115
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hvr9-wr9p-grgr
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.3.1

## Details
Mercurial prior to version 4.3 is vulnerable to a missing symlink check that can malicious repositories to modify files outside the repository

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000115
- https://access.redhat.com/errata/RHSA-2017:2489
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2017-88.yaml
- https://security.gentoo.org/glsa/201709-18
- https://web.archive.org/web/20200227155758/http://www.securityfocus.com/bid/100290
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.3_.2F_4.3.1_.282017-08-10.29
- http://www.debian.org/security/2017/dsa-3963

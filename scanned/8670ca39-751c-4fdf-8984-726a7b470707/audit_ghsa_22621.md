# [C] Mercurial is vulnerable to shell injection attack

## Summary
Severity: Critical
Advisory: GHSA-3qmg-c9vc-r47j
CVE: CVE-2017-1000116
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3qmg-c9vc-r47j
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.3

## Details
Mercurial prior to 4.3 did not adequately sanitize hostnames passed to ssh, leading to possible shell-injection attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000116
- https://access.redhat.com/errata/RHSA-2017:2489
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2017-89.yaml
- https://security.gentoo.org/glsa/201709-18
- https://web.archive.org/web/20200227155758/http://www.securityfocus.com/bid/100290
- https://wiki.mercurial-scm.org/WhatsNew/Archive
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.3_.2F_4.3.1_.282017-08-10.29
- http://www.debian.org/security/2017/dsa-3963

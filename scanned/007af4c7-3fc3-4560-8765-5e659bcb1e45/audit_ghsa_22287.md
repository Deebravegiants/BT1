# [C] Zend Framework Allows SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-xfjq-w3cw-h5fq
CVE: CVE-2016-4861
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xfjq-w3cw-h5fq
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=0 <1.12.20

## Details
The (1) order and (2) group methods in Zend_Db_Select in the Zend Framework before 1.12.20 might allow remote attackers to conduct SQL injection attacks by leveraging failure to remove comments from an SQL statement before validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4861
- https://framework.zend.com/security/advisory/ZF2016-03
- https://github.com/zendframework/zendframework
- https://lists.debian.org/debian-lts-announce/2018/06/msg00012.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2JUKFTI6ABK7ZN7IEAGPCLAHCFANMID2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N27AV6AL6B4KGEP3VIMIHQ5LFAKF5FTU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UR5HXNGIUSSIZKMSZYMPBEPZEZTYFTIT
- https://security.gentoo.org/glsa/201804-10
- http://jvn.jp/en/jp/JVN18926672/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2016-000158

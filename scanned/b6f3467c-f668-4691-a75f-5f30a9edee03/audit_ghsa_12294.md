# [H] archive-tar-minitar and minitar vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-h5g2-38x9-4gv3
CVE: CVE-2016-10173
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-h5g2-38x9-4gv3
Type: github-advisory

## Affected
- RubyGems: `archive-tar-minitar` — affected >=0 <0.5.2
- RubyGems: `minitar` — affected >=0 <0.6

## Details
Directory traversal vulnerability in the minitar before 0.6 and archive-tar-minitar 0.5.2 gems for Ruby allows remote attackers to write to arbitrary files via a `..` (dot dot) in a TAR archive entry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10173
- https://github.com/halostatue/minitar/issues/16
- https://github.com/halostatue/minitar/commit/e25205ecbb6277ae8a3df1e6a306d7ed4458b6e4
- https://github.com/halostatue/minitar
- https://security.gentoo.org/glsa/201702-32
- https://web.archive.org/web/20170214020917/http://www.securityfocus.com/bid/95874
- https://web.archive.org/web/20201207111726/https://www.puppet.com/security/cve/cve-2016-10173
- http://www.debian.org/security/2017/dsa-3778
- http://www.openwall.com/lists/oss-security/2017/01/24/7
- http://www.openwall.com/lists/oss-security/2017/01/29/1

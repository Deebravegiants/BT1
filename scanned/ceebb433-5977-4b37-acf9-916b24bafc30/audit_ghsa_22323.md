# [M] MoinMoin Directory Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v33q-2xcj-4f3m
CVE: CVE-2012-6080
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v33q-2xcj-4f3m
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=1.9.3 <1.9.6

## Details
Directory traversal vulnerability in the `_do_attachment_move` function in the AttachFile action (`action/AttachFile.py`) in MoinMoin 1.9.3 through 1.9.5 allows remote attackers to overwrite arbitrary files via a `..` (dot dot) in a file name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6080
- https://bugs.launchpad.net/ubuntu/+source/moin/+bug/1094599
- https://github.com/moinwiki/moin
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2013-5.yaml
- https://web.archive.org/web/20130513231719/http://secunia.com/advisories/51663
- https://web.archive.org/web/20151017045319/http://secunia.com/advisories/51696
- https://web.archive.org/web/20151104192815/http://secunia.com/advisories/51676
- https://web.archive.org/web/20200228145410/http://www.securityfocus.com/bid/57076
- http://hg.moinmo.in/moin/1.9/rev/3c27131a3c52
- http://moinmo.in/SecurityFixes
- http://ubuntu.com/usn/usn-1680-1
- http://www.debian.org/security/2012/dsa-2593
- http://www.openwall.com/lists/oss-security/2012/12/30/6

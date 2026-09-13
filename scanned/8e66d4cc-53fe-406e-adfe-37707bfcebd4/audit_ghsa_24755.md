# [M] Mercurial Directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v2gw-x5jf-pgwv
CVE: CVE-2008-2942
CWE: CWE-22
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-v2gw-x5jf-pgwv
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <1.0.2

## Details
Directory traversal vulnerability in patch.py in Mercurial before 1.0.2 allows user-assisted attackers to modify arbitrary files via ".." (dot dot) sequences in a patch file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-2942
- https://exchange.xforce.ibmcloud.com/vulnerabilities/43551
- https://github.com/dscho/hg
- https://issues.rpath.com/browse/RPL-2633
- http://lists.opensuse.org/opensuse-security-announce/2008-07/msg00006.html
- http://secunia.com/advisories/31108
- http://secunia.com/advisories/31110
- http://secunia.com/advisories/31167
- http://security.gentoo.org/glsa/glsa-200807-09.xml
- http://wiki.rpath.com/Advisories:rPSA-2008-0211
- http://www.openwall.com/lists/oss-security/2008/06/30/1
- http://www.openwall.com/lists/oss-security/2008/07/01/1
- http://www.securityfocus.com/archive/1/493881/100/0/threaded
- http://www.securityfocus.com/bid/30072
- http://www.selenic.com/hg/rev/87c704ac92d4

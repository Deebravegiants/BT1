# [M] Roundup Directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q7mf-hp9m-cx6f
CVE: CVE-2004-1444
CWE: CWE-22
Ecosystem: PyPI
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-q7mf-hp9m-cx6f
Type: github-advisory

## Affected
- PyPI: `Roundup` — affected >=0 <0.7.3

## Details
Directory traversal vulnerability in Roundup 0.6.4 and earlier allows remote attackers to view arbitrary files via `..` (dot dot) sequences in an `@@` command in an HTTP GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2004-1444
- https://exchange.xforce.ibmcloud.com/vulnerabilities/16350
- https://github.com/roundup-tracker/roundup
- http://packetstormsecurity.nl/0406-exploits/roundUP.txt
- http://secunia.com/advisories/11801
- http://securitytracker.com/id?1010415
- http://sourceforge.net/tracker/index.php?func=detail&aid=961511&group_id=31577&atid=402788
- http://www.gentoo.org/security/en/glsa/glsa-200408-09.xml
- http://www.securityfocus.com/bid/10495

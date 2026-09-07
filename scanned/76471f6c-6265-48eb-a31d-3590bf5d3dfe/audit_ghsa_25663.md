# [M] Mailman Cross-site scripting (XSS) vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-82rm-28q9-435p
CVE: CVE-2003-0038
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-82rm-28q9-435p
Type: github-advisory

## Affected
- PyPI: `mailman` — affected >=0 <2.1.1

## Details
Cross-site scripting (XSS) vulnerability in options.py for Mailman 2.1 allows remote attackers to inject script or HTML into web pages via the (1) email or (2) language parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2003-0038
- https://exchange.xforce.ibmcloud.com/vulnerabilities/11152
- http://marc.info/?l=bugtraq&m=104342745916111
- http://telia.dl.sourceforge.net/sourceforge/mailman/xss-2.1.0-patch.txt
- http://www.debian.org/security/2004/dsa-436
- http://www.osvdb.org/9205
- http://www.securityfocus.com/bid/6677
- http://www.securitytracker.com/id?1005987

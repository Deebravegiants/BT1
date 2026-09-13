# [M] Plone credentials stored in session cookie

## Summary
Severity: Medium
Advisory: GHSA-hjp5-hv33-q58g
CVE: CVE-2008-1396
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-hjp5-hv33-q58g
Type: github-advisory

## Affected
- PyPI: `plone` — affected >=0

## Details
Plone CMS 3.1.x uses invariant data (a client username and a server secret) when calculating an HMAC-SHA1 value for an authentication cookie, which makes it easier for remote attackers to gain permanent access to an account by sniffing the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1396
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41421
- https://github.com/plone/Plone
- http://securityreason.com/securityalert/3754
- http://www.procheckup.com/Hacking_Plone_CMS.pdf
- http://www.securityfocus.com/archive/1/489544/100/0/threaded

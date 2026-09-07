# [H] Plone CMS Improper Session Management

## Summary
Severity: High
Advisory: GHSA-mq3q-jjph-rp5p
CVE: CVE-2008-1394
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-mq3q-jjph-rp5p
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <3.0

## Details
Plone CMS before 3 places a base64 encoded form of the username and password in the `__ac` cookie for all user accounts, which makes it easier for remote attackers to obtain access by sniffing the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1394
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41425
- https://github.com/plone/Plone
- http://plone.org/about/security/overview/security-overview-of-plone
- http://securityreason.com/securityalert/3754
- http://www.procheckup.com/Hacking_Plone_CMS.pdf
- http://www.securityfocus.com/archive/1/489544/100/0/threaded

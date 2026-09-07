# [M] Cobbler XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q9g5-98pm-w6q7
CVE: CVE-2018-1000225
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q9g5-98pm-w6q7
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0

## Details
Cobbler version Verified as present in Cobbler versions 2.6.11+, but code inspection suggests at least 2.0.0+ or possibly even older versions may be vulnerable contains a Cross Site Scripting (XSS) vulnerability in cobbler-web that can result in Privilege escalation to admin.. This attack appear to be exploitable via "network connectivity". Sending unauthenticated JavaScript payload to the Cobbler XMLRPC API (/cobbler_api).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000225
- https://github.com/cobbler/cobbler/issues/1917
- https://github.com/cobbler/cobbler
- https://github.com/cobbler/cobbler/blob/master/cobbler/remote.py#L2236
- https://movermeyer.com/2018-08-02-privilege-escalation-exploits-in-cobblers-api

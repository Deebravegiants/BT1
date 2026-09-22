# [C] Cobbler Improper Validation of Security Tokens

## Summary
Severity: Critical
Advisory: GHSA-f88q-22g8-frcg
CVE: CVE-2018-1000226
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-f88q-22g8-frcg
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <3.0.0

## Details
Cobbler version Verified as present in Cobbler versions 2.6.11+, but code inspection suggests at least 2.0.0+ or possibly even older versions may be vulnerable contains a Incorrect Access Control vulnerability in XMLRPC API (/cobbler_api) that can result in Privilege escalation, data manipulation or exfiltration, LDAP credential harvesting. This attack appear to be exploitable via "network connectivity". Taking advantage of improper validation of security tokens in API endpoints. Please note this is a different issue than CVE-2018-10931.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000226
- https://github.com/cobbler/cobbler/issues/1916
- https://github.com/cobbler/cobbler
- https://movermeyer.com/2018-08-02-privilege-escalation-exploits-in-cobblers-api

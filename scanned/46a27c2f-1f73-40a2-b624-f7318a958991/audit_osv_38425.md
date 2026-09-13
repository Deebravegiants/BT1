# [H] LDAP injection in MISP ApacheAuthenticate when using a user-controlled Apache environment variable

## Summary
Severity: High
Advisory: CVE-2026-39962
Aliases: GHSA-mc53-48w8-9g63
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:L/SC:H/SI:H/SA:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39962
Type: osv

## Details
MISP is an open source threat intelligence and sharing platform. Prior to 2.5.36, improper neutralization of special elements in an LDAP query in ApacheAuthenticate.php allows LDAP injection via an unsanitized username value when ApacheAuthenticate.apacheEnv is configured to use a user-controlled server variable instead of REMOTE_USER (such as in certain proxy setups). An attacker able to control that value can manipulate the LDAP search filter and potentially bypass authentication constraints or cause unauthorized LDAP queries. This vulnerability is fixed in 2.5.36.

## References
- https://github.com/MISP/MISP/releases/tag/v2.5.36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39962.json
- https://github.com/MISP/MISP/security/advisories/GHSA-mc53-48w8-9g63
- https://nvd.nist.gov/vuln/detail/CVE-2026-39962
- https://github.com/MISP/MISP/commit/380ee4136a7d9ce2fe63fce06d517839f30aba10
- https://github.com/MISP/MISP/commit/d7d671ea8f5822e91207dcad2003c35c30092a32

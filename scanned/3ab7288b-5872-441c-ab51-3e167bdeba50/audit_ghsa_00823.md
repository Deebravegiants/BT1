# [H] LDAP Injection in ldapauth

## Summary
Severity: High
Advisory: GHSA-82mg-x548-gq3j
CVE: CVE-2015-7294
CWE: CWE-90
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-82mg-x548-gq3j
Type: github-advisory

## Affected
- npm: `ldapauth-fork` — affected >=0 <2.3.3
- npm: `ldapauth` — affected >=0

## Details
Versions 2.2.4 and earlier of `ldapauth-fork` are affected by an LDAP injection vulnerability. This allows an attacker to inject and run arbitrary LDAP commands via the username parameter.



## Recommendation

ldapauth is not actively maintained, having not seen a publish since 2014. As a result, there is no patch available. Consider updating to use [ldapauth-fork](https://www.npmjs.com/package/ldapauth-fork) 2.3.3 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7294
- https://github.com/vesse/node-ldapauth-fork/issues/21
- https://github.com/vesse/node-ldapauth-fork/commit/3feea43e243698bcaeffa904a7324f4d96df60e4
- https://github.com/vesse/node-ldapauth-fork
- https://www.npmjs.com/advisories/18
- https://www.npmjs.com/advisories/19
- http://www.openwall.com/lists/oss-security/2015/09/18/4
- http://www.openwall.com/lists/oss-security/2015/09/18/8
- http://www.openwall.com/lists/oss-security/2015/09/21/2

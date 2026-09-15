# [M] Improper Authentication in OpenSAML

## Summary
Severity: Medium
Advisory: GHSA-qwwj-qj3f-9hv7
CVE: CVE-2011-1411
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qwwj-qj3f-9hv7
Type: github-advisory

## Affected
- Maven: `org.opensaml:opensaml` — affected >=2.4.0 <2.4.3
- Maven: `org.opensaml:opensaml` — affected >=2.5.0 <2.5.1

## Details
Shibboleth OpenSAML library 2.4.x before 2.4.3 and 2.5.x before 2.5.1, and IdP before 2.3.2, allows remote attackers to forge messages and bypass authentication via an "XML Signature wrapping attack."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1411
- http://shibboleth.internet2.edu/secadv/secadv_20110725.txt
- http://www.debian.org/security/2011/dsa-2284
- http://www.oracle.com/technetwork/topics/security/cpuoct2012-1515893.html

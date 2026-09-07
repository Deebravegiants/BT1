# [M] Improper Validation of Certificate with Host Mismatch in Shibboleth Identity Provider and OpenSAML Java

## Summary
Severity: Medium
Advisory: GHSA-rm7v-gqfg-p2wc
CVE: CVE-2014-3603
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rm7v-gqfg-p2wc
Type: github-advisory

## Affected
- Maven: `edu.internet2.middleware:shibboleth-identityprovider` — affected >=0 <2.4.1
- Maven: `org.opensaml:opensaml` — affected >=0 <2.6.2

## Details
The (1) HttpResource and (2) FileBackedHttpResource implementations in Shibboleth Identity Provider (IdP) before 2.4.1 and OpenSAML Java 2.6.2 do not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3603
- https://bugzilla.redhat.com/show_bug.cgi?id=1131823
- http://shibboleth.net/community/advisories/secadv_20140813.txt

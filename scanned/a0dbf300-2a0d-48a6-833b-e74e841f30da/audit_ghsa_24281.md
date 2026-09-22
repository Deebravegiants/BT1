# [M] Improper Certificate Validation in vt-ldap

## Summary
Severity: Medium
Advisory: GHSA-273v-g3x4-r3rc
CVE: CVE-2014-3607
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-273v-g3x4-r3rc
Type: github-advisory

## Affected
- Maven: `edu.vt.middleware:vt-ldap` — affected >=0 <3.3.8
- Maven: `edu.internet2.middleware:shibboleth-identityprovider` — affected >=0 <2.4.2

## Details
DefaultHostnameVerifier in Ldaptive (formerly vt-ldap) does not properly verify that the server hostname matches a domain name in the subject's Common Name (CN) field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3607
- https://bugzilla.redhat.com/show_bug.cgi?id=1140438
- https://code.google.com/archive/p/vt-middleware/issues/226
- https://code.google.com/archive/p/vt-middleware/issues/227
- https://code.google.com/archive/p/vt-middleware/issues/228
- https://code.google.com/archive/p/vt-middleware/source/default/commits
- https://code.google.com/p/vt-middleware/source/detail?r=3046
- http://shibboleth.net/community/advisories/secadv_20140919.txt

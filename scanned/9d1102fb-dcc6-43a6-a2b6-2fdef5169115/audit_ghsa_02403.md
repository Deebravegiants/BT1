# [H] Improper Authentication in Apereo CAS

## Summary
Severity: High
Advisory: GHSA-q39c-5vh5-vw2p
CVE: CVE-2020-27178
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-q39c-5vh5-vw2p
Type: github-advisory

## Affected
- Maven: `org.apereo.cas:cas-server-webapp` — affected >=5.3.0 <5.3.16
- Maven: `org.apereo.cas:cas-server-webapp` — affected >=6.0.0 <6.1.7.2
- Maven: `org.apereo.cas:cas-server-webapp` — affected >=6.2.0 <6.2.4
- Maven: `org.apereo.cas:cas-server-support-otp-mfa-core` — affected >=5.3.0 <5.3.16
- Maven: `org.apereo.cas:cas-server-support-otp-mfa-core` — affected >=6.0.0 <6.1.7.2
- Maven: `org.apereo.cas:cas-server-support-otp-mfa-core` — affected >=6.2.0 <6.2.4

## Details
Apereo CAS 5.3.x before 5.3.16, 6.x before 6.1.7.2, 6.2.x before 6.2.4, and 6.3.x before 6.3.0-RC4 mishandles secret keys with Google Authenticator for multifactor authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27178
- https://apereo.github.io/2020/10/14/gauthvuln

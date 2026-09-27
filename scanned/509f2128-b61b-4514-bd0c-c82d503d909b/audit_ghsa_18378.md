# [M] Jakarta Mail vulnerable to SMTP Injection

## Summary
Severity: Medium
Advisory: GHSA-9342-92gg-6v29
CVE: CVE-2025-7962
CWE: CWE-147
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-9342-92gg-6v29
Type: github-advisory

## Affected
- Maven: `org.eclipse.angus:smtp` — affected >=0 <2.0.4
- Maven: `com.sun.mail:jakarta.mail` — affected >=0 <1.6.8
- Maven: `com.sun.mail:jakarta.mail` — affected >=2.0.0 <2.0.2

## Details
In Jakarta Mail 2.2 it is possible to preform a SMTP Injection by utilizing the \r and \n UTF-8 characters to separate different messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7962
- https://github.com/jakartaee/mail-api/issues/765
- https://github.com/jakartaee/mail-api/pull/760
- https://github.com/eclipse-ee4j/angus-mail/commit/269099b652a0a5c2fa140f1296a18f0fbbea0d44
- https://github.com/eclipse-ee4j/angus-mail
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/67
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/290
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/290#note_5320539
- http://www.openwall.com/lists/oss-security/2025/09/03/4

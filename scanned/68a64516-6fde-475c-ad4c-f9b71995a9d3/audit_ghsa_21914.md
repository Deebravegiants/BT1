# [H] Improper Certificate Validation in Graylog

## Summary
Severity: High
Advisory: GHSA-3gg9-f3vh-866f
CVE: CVE-2020-15813
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-3gg9-f3vh-866f
Type: github-advisory

## Affected
- Maven: `org.graylog:graylog-parent` — affected >=0 <3.3.3

## Details
Graylog before 3.3.3 lacks SSL Certificate Validation for LDAP servers. It allows use of an external user/group database stored in LDAP. The connection configuration allows the usage of unencrypted, SSL- or TLS-secured connections. Unfortunately, the Graylog client code (in all versions that support LDAP) does not implement proper certificate validation (regardless of whether the "Allow self-signed certificates" option is used). Therefore, any attacker with the ability to intercept network traffic between a Graylog server and an LDAP server is able to redirect traffic to a different LDAP server (unnoticed by the Graylog server due to the lack of certificate validation), effectively bypassing Graylog's authentication mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15813
- https://github.com/Graylog2/graylog2-server/issues/5906
- https://github.com/Graylog2/graylog2-server/pull/8569

# [H] Apache SeaTunnel Web Authentication vulnerability

## Summary
Severity: High
Advisory: GHSA-cp2c-x2pc-fph7
CVE: CVE-2023-48396
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-07-30
Source: https://github.com/advisories/GHSA-cp2c-x2pc-fph7
Type: github-advisory

## Affected
- Maven: `org.apache.seatunnel:seatunnel-web` — affected >=0 <1.0.1

## Details
Web Authentication vulnerability in Apache SeaTunnel. Since the jwt key is hardcoded in the application, an attacker can forge any token to log in any user.

Attacker can get secret key in /seatunnel-server/seatunnel-app/src/main/resources/application.yml and then create a token. This issue affects Apache SeaTunnel: 1.0.0.

Users are recommended to upgrade to version 1.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48396
- https://github.com/apache/seatunnel-web/commit/4a37ebfa4b57e177bf7857cf39a6dbdc00f75f78
- https://github.com/apache/seatunnel
- https://lists.apache.org/thread/1tdxfjksx0vb9gtyt77wlr6rdcy1qwmw
- http://www.openwall.com/lists/oss-security/2024/07/30/1

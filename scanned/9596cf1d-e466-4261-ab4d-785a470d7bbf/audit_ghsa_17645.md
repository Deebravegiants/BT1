# [M] Spring Framework vulnerable to a reflected file download (RFD)

## Summary
Severity: Medium
Advisory: GHSA-6r3c-xf4w-jxjm
CVE: CVE-2025-41234
CWE: CWE-113
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-6r3c-xf4w-jxjm
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=6.2.0 <6.2.8
- Maven: `org.springframework:spring-web` — affected >=6.1.0 <6.1.21
- Maven: `org.springframework:spring-web` — affected >=6.0.5

## Details
### Description

In Spring Framework, versions 6.0.x as of 6.0.5, versions 6.1.x and 6.2.x, an application is vulnerable to a reflected file download (RFD) attack when it sets a “Content-Disposition” header with a non-ASCII charset, where the filename attribute is derived from user-supplied input.

Specifically, an application is vulnerable when all the following are true:

  -  The header is prepared with `org.springframework.http.ContentDisposition`.
  -  The filename is set via `ContentDisposition.Builder#filename(String, Charset)`.
  -  The value for the filename is derived from user-supplied input.
  -  The application does not sanitize the user-supplied input.
  -  The downloaded content of the response is injected with malicious commands by the attacker (see RFD paper reference for details).


An application is not vulnerable if any of the following is true:

  -  The application does not set a “Content-Disposition” response header.
  -  The header is not prepared with `org.springframework.http.ContentDisposition`.
  -  The filename is set via one of:  
     - `ContentDisposition.Builder#filename(String)`, or
     - `ContentDisposition.Builder#filename(String, ASCII)`
  -  The filename is not derived from user-supplied input.
  -  The filename is derived from user-supplied input but sanitized by the application.
  -  The attacker cannot inject malicious content in the downloaded content of the response.


### Affected Spring Products and VersionsSpring Framework

  -  6.2.0 - 6.2.7
  -  6.1.0 - 6.1.20
  -  6.0.5 - 6.0.28
  -  Older, unsupported versions are not affected


### Mitigation

Users of affected versions should upgrade to the corresponding fixed version.

| Affected version(s) | Fix version | Availability |
| - | - | - |
| 6.2.x | 6.2.8 | OSS |
| 6.1.x | 6.1.21 | OSS |
| 6.0.x | 6.0.29 | [Commercial](https://enterprise.spring.io/) |

No further mitigation steps are necessary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41234
- https://github.com/spring-projects/spring-framework/issues/35034
- https://github.com/spring-projects/spring-framework/commit/f0e7b42704e6b33958f242d91bd690d6ef7ada9c
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2025-41234

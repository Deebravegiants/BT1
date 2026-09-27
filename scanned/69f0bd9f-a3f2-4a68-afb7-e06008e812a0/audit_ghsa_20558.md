# [H] Missing Authentication for Critical Function in Apache NiFi

## Summary
Severity: High
Advisory: GHSA-3pp3-77j6-8ph6
CVE: CVE-2020-9487
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-3pp3-77j6-8ph6
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.12.0-RC1

## Details
In Apache NiFi 1.0.0 to 1.11.4, the NiFi download token (one-time password) mechanism used a fixed cache size and did not authenticate a request to create a download token, only when attempting to use the token to access the content. An unauthenticated user could repeatedly request download tokens, preventing legitimate users from requesting download tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9487
- https://github.com/apache/nifi/commit/01e42dfb3291c3a3549023edadafd2d8023f3042
- https://nifi.apache.org/security#CVE-2020-9487

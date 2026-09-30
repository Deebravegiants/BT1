# [H] Spring Cloud Config Server Susceptible To TOCTOU Attack When Using SVN

## Summary
Severity: High
Advisory: CVE-2026-47836
CVSS: 7.2 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47836
Type: osv

## Details
The base directory (spring.cloud.config.server.svn.basedir) used by the Spring Cloud Config Server to clone SVN repositories to is susceptible to time-of-check-time-of-use (TOCTOU) attacks.
Spring Cloud Config 5.0.0 - 5.0.4
Spring Cloud Config 4.3.0 - 4.3.4
Spring Cloud Config 4.0.0 - 4.2.8
Spring Cloud Config 3.1.14 and earlier

## References
- https://spring.io/security/cve-2026-47836
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47836.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47836

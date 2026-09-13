# [H] Tugtainer vulnerable to Password Exposure via URL Query Parameter

## Summary
Severity: High
Advisory: CVE-2026-23846
Aliases: GHSA-f2qf-f544-xm4p
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23846
Type: osv

## Details
Tugtainer is a self-hosted app for automating updates of Docker containers. In versions prior to 1.16.1, the password authentication mechanism transmits passwords via URL query parameters instead of the HTTP request body. This causes passwords to be logged in server access logs and potentially exposed through browser history, Referer headers, and proxy logs. Version 1.16.1 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23846.json
- https://github.com/Quenary/tugtainer/security/advisories/GHSA-f2qf-f544-xm4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-23846
- https://github.com/Quenary/tugtainer/commit/9d23bf40ac1d39005582abfcf0a84753a4e29d52

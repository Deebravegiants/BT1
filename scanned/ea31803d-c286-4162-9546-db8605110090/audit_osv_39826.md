# [C] Tugtainer has Server-Side Template Injection in notification templates that leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-47752
Aliases: GHSA-g2cj-2x47-78vq
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-47752
Type: osv

## Details
Tugtainer is a self-hosted app for automating updates of Docker containers. Versions prior to 1.30.2 are vulnerable to Server-Side Template Injection (SSTI) in the notification template feature. The `title_template` and `body_template` fields are rendered using an unsandboxed `jinja2.Environment`, allowing any authenticated user to execute arbitrary OS commands as root inside the container. Version 1.30.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47752.json
- https://github.com/Quenary/tugtainer/security/advisories/GHSA-g2cj-2x47-78vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47752

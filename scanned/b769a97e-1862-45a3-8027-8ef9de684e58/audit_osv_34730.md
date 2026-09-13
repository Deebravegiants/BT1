# [C] Colify has command injection vulnerability in project git source

## Summary
Severity: Critical
Advisory: CVE-2025-64424
Aliases: GHSA-qx24-jhwj-8w6x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-64424
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. In Coolify versions up to and including v4.0.0-beta.434, a command injection vulnerability exists in the git source input fields of a resource, allowing a low privileged user (member) to execute system commands as root on the Coolify instance. As of time of publication, it is unclear if a patch is available.

## References
- https://drive.google.com/file/d/1rk7AYxNDkJUwo8uWbzX62PpBxpDYeyrZ/view?usp=drive_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64424.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-qx24-jhwj-8w6x
- https://nvd.nist.gov/vuln/detail/CVE-2025-64424

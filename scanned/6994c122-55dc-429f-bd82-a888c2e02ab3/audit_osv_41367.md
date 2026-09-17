# [H] Coolify: OS Command Injection in Health Check Configuration Allows Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-59734
Aliases: GHSA-4fhp-xqqp-w7vv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59734
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.469, Coolify's app/Jobs/ApplicationDeploymentJob.php generate_healthcheck_commands() function directly interpolated the health_check_host, health_check_method, and health_check_path parameters into shell commands without proper sanitization, allowing authenticated users to execute arbitrary commands inside deployment containers. This issue is fixed in version 4.0.0-beta.469.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.469
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59734.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-4fhp-xqqp-w7vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-59734
- https://github.com/coollabsio/coolify/commit/0ffcee7a4dcd24f92b5fab8c9c7be140b9532733
- https://github.com/coollabsio/coolify/pull/9007

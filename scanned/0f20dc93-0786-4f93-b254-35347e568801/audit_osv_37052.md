# [M] Coolify: Command Injection via Single-Quote Breakout in `executeInDocker()`

## Summary
Severity: Medium
Advisory: CVE-2026-27955
Aliases: GHSA-6h8g-wpxp-cq98
CVSS: 6.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-27955
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, the executeInDocker() helper wraps commands in bash -c '{$command}' without escaping single quotes. User-controlled docker_compose_custom_build_command and docker_compose_custom_start_command fields are interpolated directly, allowing a single quote to break out of the bash -c argument and execute commands on the managed server host (outside the intended Docker container context). This vulnerability is fixed in 4.0.0-beta.464.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27955.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-6h8g-wpxp-cq98
- https://nvd.nist.gov/vuln/detail/CVE-2026-27955

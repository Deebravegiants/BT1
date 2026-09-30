# [H] Nuclio: Unauthenticated OS command injection via function namespace in docker ps --filter label (local Docker platform)

## Summary
Severity: High
Advisory: CVE-2026-79755
Aliases: GHSA-2893-rq73-w22x
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-79755
Type: osv

## Details
Nuclio is a "Serverless" framework for Real-Time Events and Data Processing. Prior to version 1.17.4, on the Nuclio local Docker platform, the function namespace is interpolated—unvalidated—into a double-quoted docker ps --filter "label=nuclio.io/namespace=<value>" command that is executed via the host shell (/bin/sh -c). Because the default auth kind is nop (unauthenticated), a remote attacker can inject arbitrary OS commands that run as root inside the dashboard container, which holds the Docker socket → host compromise. This issue has been patched in version 1.17.4.

## References
- https://github.com/nuclio/nuclio/releases/tag/1.17.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79755.json
- https://github.com/nuclio/nuclio/security/advisories/GHSA-2893-rq73-w22x
- https://nvd.nist.gov/vuln/detail/CVE-2026-79755
- https://github.com/nuclio/nuclio/commit/24582ac354d04951ec6786b3fe6ccf3b32652e9f
- https://github.com/nuclio/nuclio/pull/4220

# [H] Semaphore UI: Manager-to-owner privilege escalation via custom-role slug collision

## Summary
Severity: High
Advisory: CVE-2026-73293
Aliases: GHSA-cxvf-gvfq-36w2, GO-2026-6371
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73293
Type: osv

## Details
Semaphore UI is a web interface for managing DevOps tools.  Prior to 2.18.19 and from 2.19.0-alpha3 until 2.19.5-beta5, ProjectMiddleware and GetProjectOrGlobalRoleBySlug allow a project manager to use POST /api/project/{id}/roles to create a custom manager role with permission bitmask 15, overriding the built-in manager permissions and granting CanUpdateProject and CanManageProjectUsers owner capabilities. This issue is fixed in versions 2.18.19 and 2.19.5-beta5.

## References
- https://github.com/semaphoreui/semaphore/releases/tag/v2.18.19
- https://github.com/semaphoreui/semaphore/releases/tag/v2.19.5-beta5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73293.json
- https://github.com/semaphoreui/semaphore/security/advisories/GHSA-cxvf-gvfq-36w2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73293
- https://github.com/semaphoreui/semaphore/commit/1c4bb65df114962134f8829d4a03667106a01a68
- https://github.com/semaphoreui/semaphore/commit/bb2a4e1f08c8023e618f8dd6eaca73554f2c33bb

# [H] OpenChoreo: Cross-project command execution and wirelog view access via OpenChoreo openchoreo-api exec and wirelogs endpoints

## Summary
Severity: High
Advisory: CVE-2026-73841
Aliases: GHSA-52gf-6rpq-fgmx, GO-2026-6358
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73841
Type: osv

## Details
OpenChoreo is a complete, open-source developer platform for Kubernetes. Prior to 1.1.6 and 1.2.3, internal/openchoreo-api/api/handlers/exec.go and internal/openchoreo-api/api/handlers/wirelogs.go authorize component:exec and wirelogs:view using the caller-supplied project query parameter instead of comp.Spec.Owner.ProjectName, allowing a user with a project-scoped grant to execute commands in and read wirelogs from components owned by other projects in the same namespace. This vulnerability is fixed in 1.1.6 and 1.2.3.

## References
- https://github.com/openchoreo/openchoreo/releases/tag/v1.1.6
- https://github.com/openchoreo/openchoreo/releases/tag/v1.2.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73841.json
- https://github.com/openchoreo/openchoreo/security/advisories/GHSA-52gf-6rpq-fgmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-73841
- https://github.com/openchoreo/openchoreo/commit/4d372eaf1f07525663dcca5257062f4b051b9820
- https://github.com/openchoreo/openchoreo/commit/9d77b64f747eba89247c47ebfeffec591c4cd2d8
- https://github.com/openchoreo/openchoreo/commit/c9390e4fcb9953f43b07cb48197576182301593d
- https://github.com/openchoreo/openchoreo/pull/4251
- https://github.com/openchoreo/openchoreo/pull/4516
- https://github.com/openchoreo/openchoreo/pull/4538

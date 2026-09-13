# [H] pnpm v10+ Bypass "Dependency lifecycle scripts execution disabled by default"

## Summary
Severity: High
Advisory: CVE-2025-69264
Aliases: GHSA-379q-355j-w6rj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-69264
Type: osv

## Details
pnpm is a package manager. Versions 10.0.0 through 10.25 allow git-hosted dependencies to execute arbitrary code during pnpm install, circumventing the v10 security feature "Dependency lifecycle scripts execution disabled by default". While pnpm v10 blocks postinstall scripts via the onlyBuiltDependencies mechanism, git dependencies can still execute prepare, prepublish, and prepack scripts during the fetch phase, enabling remote code execution without user consent or approval. This issue is fixed in version 10.26.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-69264.json
- https://access.redhat.com/security/cve/CVE-2025-69264
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69264.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-379q-355j-w6rj
- https://nvd.nist.gov/vuln/detail/CVE-2025-69264
- https://bugzilla.redhat.com/show_bug.cgi?id=2427709
- https://github.com/pnpm/pnpm/commit/73cc63504d9bc360c43e4b2feb9080677f03c5b5

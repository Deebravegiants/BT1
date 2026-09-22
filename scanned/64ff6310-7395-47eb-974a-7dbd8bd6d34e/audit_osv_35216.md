# [H] pnpm Lockfile Integrity Bypass Allows Remote Dynamic Dependencies

## Summary
Severity: High
Advisory: CVE-2025-69263
Aliases: GHSA-7vhp-vf5g-r2fw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-69263
Type: osv

## Details
pnpm is a package manager. Versions 10.26.2 and below store HTTP tarball dependencies (and git-hosted tarballs) in the lockfile without integrity hashes. This allows the remote server to serve different content on each install, even when a lockfile is committed. An attacker who publishes a package with an HTTP tarball dependency can serve different code to different users or CI/CD environments. The attack requires the victim to install a package that has an HTTP/git tarball in its dependency tree. The victim's lockfile provides no protection. This issue is fixed in version 10.26.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-69263.json
- https://access.redhat.com/security/cve/CVE-2025-69263
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69263.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-7vhp-vf5g-r2fw
- https://nvd.nist.gov/vuln/detail/CVE-2025-69263
- https://bugzilla.redhat.com/show_bug.cgi?id=2427703
- https://github.com/pnpm/pnpm/commit/0958027f88a99ccefe7e9676cdebba393dfbdc85

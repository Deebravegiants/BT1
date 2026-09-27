# [M] pnpm has symlink traversal in file:/git dependencies

## Summary
Severity: Medium
Advisory: CVE-2026-24056
Aliases: GHSA-m733-5w8f-5ggw
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-24056
Type: osv

## Details
pnpm is a package manager. Prior to version 10.28.2, when pnpm installs a `file:` (directory) or `git:` dependency, it follows symlinks and reads their target contents without constraining them to the package root. A malicious package containing a symlink to an absolute path (e.g., `/etc/passwd`, `~/.ssh/id_rsa`) causes pnpm to copy that file's contents into `node_modules`, leaking local data. The vulnerability only affects `file:` and `git:` dependencies. Registry packages (npm) have symlinks stripped during publish and are NOT affected. The issue impacts developers installing local/file dependencies andCI/CD pipelines installing git dependencies. It can lead to credential theft via symlinks to `~/.aws/credentials`, `~/.npmrc`, `~/.ssh/id_rsa`. Version 10.28.2 contains a patch.

## References
- https://github.com/pnpm/pnpm/releases/tag/v10.28.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24056.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-m733-5w8f-5ggw
- https://nvd.nist.gov/vuln/detail/CVE-2026-24056
- https://github.com/pnpm/pnpm/commit/b277b45bc35ae77ca72d7634d144bbd58a48b70f

# [M] pnpm has Path Traversal via arbitrary file permission modification

## Summary
Severity: Medium
Advisory: CVE-2026-24131
Aliases: GHSA-v253-rj99-jwpq
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-24131
Type: osv

## Details
pnpm is a package manager. Prior to version 10.28.2, when pnpm processes a package's `directories.bin` field, it uses `path.join()` without validating the result stays within the package root. A malicious npm package can specify `"directories": {"bin": "../../../../tmp"}` to escape the package directory, causing pnpm to chmod 755 files at arbitrary locations. This issue only affects Unix/Linux/macOS. Windows is not affected (`fixBin` gated by `EXECUTABLE_SHEBANG_SUPPORTED`). Version 10.28.2 contains a patch.

## References
- https://github.com/pnpm/pnpm/releases/tag/v10.28.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24131.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-v253-rj99-jwpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-24131
- https://github.com/pnpm/pnpm/commit/17432ad5bbed5c2e77255ca6d56a1449bbcfd943

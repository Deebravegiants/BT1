# [M] pnpm scoped bin name Path Traversal allows arbitrary file creation outside node_modules/.bin

## Summary
Severity: Medium
Advisory: CVE-2026-23890
Aliases: GHSA-xpqm-wm3m-f34h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-23890
Type: osv

## Details
pnpm is a package manager. Prior to version 10.28.1, a path traversal vulnerability in pnpm's bin linking allows malicious npm packages to create executable shims or symlinks outside of `node_modules/.bin`. Bin names starting with `@` bypass validation, and after scope normalization, path traversal sequences like `../../` remain intact. This issue affects all pnpm users who install npm packages and CI/CD pipelines using pnpm. It can lead to overwriting config files, scripts, or other sensitive files. Version 10.28.1 contains a patch.

## References
- https://github.com/pnpm/pnpm/releases/tag/v10.28.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23890.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-xpqm-wm3m-f34h
- https://nvd.nist.gov/vuln/detail/CVE-2026-23890
- https://github.com/pnpm/pnpm/commit/8afbb1598445d37985d91fda18abb4795ae5062d

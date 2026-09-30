# [H] pnpm: Virtual store linker path traversal via unvalidated depPath name in lockfileToDepGraph

## Summary
Severity: High
Advisory: CVE-2026-82392
Aliases: GHSA-c59q-g84q-2gj5
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82392
Type: osv

## Details
pnpm is a package manager. Prior to 10.34.5 and from 11.0.0 until 11.11.0, pnpm parses the package name from attacker-controlled pnpm-lock.yaml packages keys with dp.parse(depPath).name and uses it without validation in deps/graph-builder/src/lockfileToDepGraph.ts and pnpm11/deps/graph-builder/src/lockfileToDepGraph.ts. The name reaches path.join(modules, pkgName), storeController.importPackage, and pnpm11/lockfile/to-pnp/src/index.ts, allowing package contents to be written outside node_modules when a user runs pnpm install. When dangerouslyAllowAllBuilds or a matching allowBuilds entry permits lifecycle scripts, the escaped package can execute code with the user's privileges. This issue is fixed in versions 10.34.5 and 11.11.0.

## References
- https://github.com/pnpm/pnpm/releases/tag/v10.34.5
- https://github.com/pnpm/pnpm/releases/tag/v11.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82392.json
- https://github.com/pnpm/pnpm/security/advisories/GHSA-c59q-g84q-2gj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-82392
- https://github.com/pnpm/pnpm/commit/51300fd41c5e4c8f47635108e373cc3d1f324fa7
- https://github.com/pnpm/pnpm/commit/78e29fe5583a1e5d69ea05e414eff310f78d5ed9
- https://github.com/pnpm/pnpm/pull/12872
- https://github.com/pnpm/pnpm/pull/12890

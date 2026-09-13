# [M] zx Uses Incorrectly-Resolved Name or Reference

## Summary
Severity: Medium
Advisory: GHSA-w87r-vg9q-crqm
CVE: CVE-2025-13437
CWE: CWE-706
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H/E:U (CVSS_V4)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-w87r-vg9q-crqm
Type: github-advisory

## Affected
- npm: `zx` — affected >=0 <8.8.5

## Details
When zx is invoked with --prefer-local=<path>, the CLI creates a symlink named ./node_modules pointing to <path>/node_modules. Due to a logic error in src/cli.ts (linkNodeModules / cleanup), the function returns the target path instead of the alias (symlink path). The later cleanup routine removes what it received, which deletes the target directory itself. Result: zx can delete an external <path>/node_modules outside the current working directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13437
- https://github.com/google/zx/issues/1348
- https://github.com/google/zx/pull/1349
- https://github.com/google/zx/pull/1355
- https://github.com/google/zx/commit/9ef6d3c9962c4ba01e3fb8075855570c192b4681
- https://github.com/google/zx/commit/a4d1bc2467f305f1c91d62506e215f307dc1fbeb
- https://github.com/google/zx

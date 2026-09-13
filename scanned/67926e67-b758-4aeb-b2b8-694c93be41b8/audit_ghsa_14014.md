# [H] Missing "--allow-net" permission check for built-in Node modules

## Summary
Severity: High
Advisory: GHSA-vc52-gwm3-8v2f
CVE: CVE-2023-33966
CWE: CWE-269, CWE-276
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-31
Source: https://github.com/advisories/GHSA-vc52-gwm3-8v2f
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.34.0 <1.34.1
- crates.io: `deno_runtime` — affected >=0.114.0 <0.115.0

## Details
### Impact

Outbound HTTP requests made using the built-in "node:http" or "node:https" modules are incorrectly not checked against the network permission allow list (`--allow-net`). Dependencies relying on these built-in modules are subject to the vulnerability too.

Users of Deno versions prior to 1.34.0 are unaffected. Deno Deploy users are unaffected.

### Patches

This problem has been patched in Deno v1.34.1 and all users are recommended to update to this version.

### Workarounds

No workaround is available for this issue.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-vc52-gwm3-8v2f
- https://nvd.nist.gov/vuln/detail/CVE-2023-33966
- https://github.com/denoland/deno
- https://github.com/denoland/deno/releases/tag/v1.34.1

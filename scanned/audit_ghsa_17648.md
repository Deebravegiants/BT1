# [M] Deno run with --allow-read and --deny-read flags results in allowed

## Summary
Severity: Medium
Advisory: GHSA-xqxc-x6p3-w683
CVE: CVE-2025-48888
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-xqxc-x6p3-w683
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.41.3 <2.1.13
- crates.io: `deno` — affected >=2.2.0 <2.2.13
- crates.io: `deno` — affected >=2.3.0 <2.3.2
- crates.io: `deno_runtime` — affected >=0.150.0 <0.212.0

## Details
### Summary

`deno run --allow-read --deny-read main.ts` results in allowed, even though 'deny' should be stronger. Same with all global unary permissions given as `--allow-* --deny-*`.

### Details

Caused by the fast exit logic in #22894.

### PoC

Run the above command expecting no permissions to be passed.

### Impact

This only affects a nonsensical combination of flags, so there shouldn't be a real impact on the userbase.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-xqxc-x6p3-w683
- https://nvd.nist.gov/vuln/detail/CVE-2025-48888
- https://github.com/denoland/deno/pull/22894
- https://github.com/denoland/deno/pull/29213
- https://github.com/denoland/deno/commit/2f0fae9d9071dcaf0a689bc7097584b1b9ebc8db
- https://github.com/denoland/deno/commit/9d665572d3cd39f997e29e6daac7c1102fc5c04f
- https://github.com/denoland/deno/commit/ef315b56c26c9ef5f25284a5100d2ed525a148cf
- https://github.com/denoland/deno

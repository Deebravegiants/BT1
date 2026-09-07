# [C] Deno improperly handles resizable ArrayBuffer

## Summary
Severity: Critical
Advisory: GHSA-c25x-cm9x-qqgx
CVE: CVE-2023-28445
CWE: CWE-125, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-c25x-cm9x-qqgx
Type: github-advisory

## Affected
- crates.io: `Deno` — affected >=1.32.0 <1.32.1
- crates.io: `serde_v8` — affected >=0.87.0 <0.88.0
- crates.io: `deno_runtime` — affected >=0.102.0 <0.103.0

## Details
### Impact

[Resizable ArrayBuffers](https://github.com/tc39/proposal-resizablearraybuffer) passed to asynchronous native functions that are shrunk during the asynchronous operation could result in an out-of-bound read/write.

It is unlikely that this has been exploited in the wild, as the only version affected is Deno 1.32.0.

Deno Deploy users are not affected.

### Patches

The problem has been resolved by disabling resizable ArrayBuffers temporarily in Deno 1.32.1. A future version of Deno will re-enable resizable ArrayBuffers with a proper fix.

### Workarounds

Upgrade to Deno 1.32.1, or run with `--v8-flags=--no-harmony-rab-gsab` to disable resizable ArrayBuffers.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-c25x-cm9x-qqgx
- https://nvd.nist.gov/vuln/detail/CVE-2023-28445
- https://github.com/denoland/deno/pull/18395
- https://github.com/denoland/deno/pull/18452
- https://github.com/denoland/deno
- https://github.com/denoland/deno/releases/tag/v1.32.1

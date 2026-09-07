# [M] Wasmtime has a possible panic when lifting `flags` component value

## Summary
Severity: Medium
Advisory: GHSA-m758-wjhj-p3jq
CVE: CVE-2026-34943
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-m758-wjhj-p3jq
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <24.0.7
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Impact

Wasmtime contains a possible panic which can happen when a `flags`-typed component model value is lifted with the `Val` type. If bits are set outside of the set of flags the component model specifies that these bits should be ignored but Wasmtime will panic when this value is lifted. This panic only affects wasmtime's implementation of lifting into `Val`, not when using the `flags!` macro. This additionally only affects `flags`-typed values which are part of a WIT interface. 

This has the risk of being a guest-controlled panic within the host which Wasmtime considers a DoS vector.

### Patches

Wasmtime 24.0.7, 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.

### Workarounds

There is no workaround for this bug if a host meets the criteria to be affected. To be affected a host must be using `wasmtime::component::Val` and possibly work with a `flags` type in the component model.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-m758-wjhj-p3jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34943
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0085.html

# [M] Wasmtime: Panic when transcoding misaligned utf-16 strings

## Summary
Severity: Medium
Advisory: GHSA-jxhv-7h78-9775
CVE: CVE-2026-34942
CWE: CWE-119, CWE-129
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-jxhv-7h78-9775
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <24.0.7
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Impact

Wasmtime's implementation of transcoding strings into the Component Model's `utf16` or `latin1+utf16` encodings improperly verified the alignment of reallocated strings. This meant that unaligned pointers could be passed to the host for transcoding which would trigger a host panic. This panic is possible to trigger from malicious guests which transfer very specific strings across components with specific addresses. 

Host panics are considered a DoS vector in Wasmtime as the panic conditions are controlled by the guest in this situation.

### Patches

Wasmtime 24.0.7, 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.

### Workarounds

There is no workaround for this bug. Hosts are recommended to updated to a patched version of Wasmtime.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-jxhv-7h78-9775
- https://nvd.nist.gov/vuln/detail/CVE-2026-34942
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0092.html

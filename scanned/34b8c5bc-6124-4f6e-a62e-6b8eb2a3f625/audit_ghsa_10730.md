# [M] Wasmtime has out-of-bounds write or crash when transcoding component model strings

## Summary
Severity: Medium
Advisory: GHSA-394w-hwhg-8vgm
CVE: CVE-2026-35195
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-394w-hwhg-8vgm
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <24.0.7
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Impact

Wasmtime's implementation of transcoding strings between components contains a bug where the return value of a guest component's `realloc` is not validated before the host attempts to write through the pointer. This enables a guest to cause the host to write arbitrary transcoded string bytes to an arbitrary location up to 4GiB away from the base of linear memory. These writes on the host could hit unmapped memory or could corrupt host data structures depending on Wasmtime's configuration.

Wasmtime by default reserves 4GiB of virtual memory for a guest's linear memory meaning that this bug will by default on hosts cause the host to hit unmapped memory and abort the process due to an unhandled fault. Wasmtime can be configured, however, to reserve less memory for a guest and to remove all guard pages, so some configurations of Wasmtime may lead to corruption of data outside of a guest's linear memory, such as host data structures or other guests's linear memories. 

### Patches

Wasmtime 24.0.7, 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.

### Workarounds

There is no known workaround for this issue and affected hosts/embeddings are recommended to upgrade.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-394w-hwhg-8vgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-35195
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0091.html

# [M] Wasmtime has host panic when Winch compiler executes `table.fill`

## Summary
Severity: Medium
Advisory: GHSA-q49f-xg75-m9xw
CVE: CVE-2026-34946
CWE: CWE-248, CWE-670
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-q49f-xg75-m9xw
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Impact

Wasmtime's Winch compiler contains a vulnerability where the compilation of the `table.fill` instruction can result in a host panic. This means that a valid guest can be compiled with Winch, on any architecture, and cause the host to panic. This represents a denial-of-service vulnerability in Wasmtime due to guests being able to trigger a panic.

The specific issue is that a historical refactoring, #11254, changed how compiled code referenced tables within the `table.*` instructions. This refactoring forgot to update the Winch code paths associated as well, meaning that Winch was using the wrong indexing scheme. Due to the feature support of Winch the only problem that can result is tables being mixed up or nonexistent tables being used, meaning that the guest is limited to panicking the host (using a nonexistent table), or executing spec-incorrect behavior and modifying the wrong table.

### Patches

Wasmtime 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.

### Workarounds

Users of Cranelift are not affected by this issue, but for users of Winch there is no workaround for this bug. Hosts are recommended to updated to a patched version of Wasmtime.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-q49f-xg75-m9xw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34946
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0089.html

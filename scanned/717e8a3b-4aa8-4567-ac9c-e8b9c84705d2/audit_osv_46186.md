# [M] JLSEC-2026-777

## Summary
Severity: Medium
Advisory: JLSEC-2026-777
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/JLSEC-2026-777
Type: osv

## Affected
- Julia: `HarfBuzz_ICU_jll` — affected >=0 <100.14002.1+0
- Julia: `HarfBuzz_jll` — affected >=0 <100.14002.1+0

## Details
HarfBuzz is a text shaping engine. Prior to version 12.3.0, a null pointer dereference vulnerability exists in the SubtableUnicodesCache::create function located in `src/hb-ot-cmap-table.hh`. The function fails to check if `hb_malloc` returns NULL before using placement new to construct an object at the returned pointer address. When `hb_malloc` fails to allocate memory (which can occur in low-memory conditions or when using custom allocators that simulate allocation failures), it returns NULL. The code then attempts to call the constructor on this null pointer using placement new syntax, resulting in undefined behavior and a Segmentation Fault. This issue has been patched in version 12.3.0.

## References
- http://www.openwall.com/lists/oss-security/2026/01/11/1
- http://www.openwall.com/lists/oss-security/2026/01/12/1
- https://github.com/harfbuzz/harfbuzz/commit/1265ff8d990284f04d8768f35b0e20ae5f60daae
- https://github.com/harfbuzz/harfbuzz/security/advisories/GHSA-xvjr-f2r9-c7ww

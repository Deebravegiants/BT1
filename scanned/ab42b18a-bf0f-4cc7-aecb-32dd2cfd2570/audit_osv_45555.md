# [M] JLSEC-2026-1301

## Summary
Severity: Medium
Advisory: JLSEC-2026-1301
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1301
Type: osv

## Affected
- Julia: `libxls_jll` — affected unspecified

## Details
libxls through version 1.6.3 contains a use of uninitialized memory vulnerability in the OLE container parser. Memory allocated for the Master Sector Allocation Table (MSAT) in `read_MSAT()` is not fully initialized before being consumed by `ole2_validate_sector_chain()`, which may result in application crashes or potential information disclosure when processing a crafted XLS file

## References
- https://github.com/libxls/libxls/issues/155
- https://github.com/libxls/libxls/issues/155

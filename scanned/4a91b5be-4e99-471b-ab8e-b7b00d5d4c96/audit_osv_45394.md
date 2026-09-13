# [M] JLSEC-2026-1117

## Summary
Severity: Medium
Advisory: JLSEC-2026-1117
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1117
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
A weakness has been identified in LibRaw up to 0.22.0. This impacts the function HuffTable::initval of the file `src/decompressors/losslessjpeg.cpp` of the component JPEG DHT Parser. This manipulation of the argument bits[] causes out-of-bounds write. It is possible to initiate the attack remotely. The exploit has been made available to the public and could be used for attacks. Upgrading to version 0.22.1 will fix this issue. Patch name: a6734e867b19d75367c05f872ac26322464e3995. It is advisable to upgrade the affected component.

## References
- https://github.com/LibRaw/LibRaw/
- https://github.com/LibRaw/LibRaw/commit/a6734e867b19d75367c05f872ac26322464e3995
- https://github.com/LibRaw/LibRaw/issues/794
- https://github.com/LibRaw/LibRaw/issues/794#issuecomment-4065342499
- https://github.com/LibRaw/LibRaw/releases/tag/0.22.1
- https://github.com/biniamf/pocs/tree/main/libraw_lljpeg
- https://vuldb.com/submit/780538
- https://vuldb.com/vuln/354650
- https://vuldb.com/vuln/354650/cti

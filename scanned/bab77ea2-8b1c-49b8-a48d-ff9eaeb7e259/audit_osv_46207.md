# [M] Crafted HTJ2K compressed EXR files can trigger out of bounds reads in OpenEXR

## Summary
Severity: Medium
Advisory: JLSEC-2026-813
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/JLSEC-2026-813
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.4.4+0 <3.4.12+0

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. In versions 3.4.0 through 3.4.11, the HTJ2K (High-Throughput JPEG 2000) decoder, `ht_undo_impl()` in OpenEXRCore is vulnerable to a heap-buffer-overflow READ. The  `ht_undo_imp` function copies decoded pixels out of a per-line OpenJPH buffer using the EXR channel's declared width as the iteration count. The codestream embedded in the EXR chunk can declare different (smaller) tile/line dimensions than the EXR header advertises, but `ht_undo_impl()` does not validate this — it pulls width 32-bit samples from `cur_line-`>i32[] without checking the OpenJPH line buffer's actual length. A crafted EXR file produces a 4-byte heap-buffer-overflow READ immediately after a buffer allocated by `ojph::local::codestream::finalize_alloc()`. The bug is reachable through the standard scanline-decode entry point used by every consumer of `exr_decoding_run/Imf::checkOpenEXRFile`, including thumbnailers, asset pipelines, and the exrcheck utility — i.e. any application that opens untrusted EXR files. The result is a deterministic crash (DoS) and potential adjacent-heap leak. This issue has been fixed in version 3.4.12.

## References
- https://access.redhat.com/security/cve/CVE-2026-45696
- https://bugzilla.redhat.com/show_bug.cgi?id=2490597
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.12
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-gjpj-qv64-vwhf
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-gjpj-qv64-vwhf
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45696.json

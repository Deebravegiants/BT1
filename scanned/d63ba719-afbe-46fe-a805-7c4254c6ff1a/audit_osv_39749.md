# [M] libheif has Heap Out Of Bounds Write in unci subsystem

## Summary
Severity: Medium
Advisory: CVE-2026-47178
Aliases: GHSA-5x55-x5pf-9c6g
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47178
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. In versions 1.19.0 through 1.21.2, a crafted HEIF file (uncompressed `unci` codec, tiled, component-interleaved, 4:2:0) triggers a heap out-of-bounds write in libheif's uncompressed tile decoder. The write overwrites the C++ vtable pointer of an adjacent `unc_decoder_component_interleave` object; the next virtual call dispatches to an attacker-chosen address. Version 1.22.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47178.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-5x55-x5pf-9c6g
- https://nvd.nist.gov/vuln/detail/CVE-2026-47178

# [H] stable-diffusion.cpp has a  Heap-based Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-47747
Aliases: GHSA-mghm-5mqc-pwmp
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-47747
Type: osv

## Details
stable-diffusion.cpp is a pure C/C++ library for running diffusion model (Stable Diffusion, Flux, Wan, Qwen Image, Z-Image, and more) inference. In versions prior to master-584-0a7ae07, the pickle .ckpt parser in src/model.cpp contained a heap buffer overflow vulnerability in the BINUNICODE opcode handler. The issue was caused by sign confusion on the opcode length field. A crafted .ckpt file could trigger memcpy with a very large length derived from a negative signed value, causing immediate heap corruption.
The issue has been resolved in version master-584-0a7ae07. If developers are unable to immediately update their applications they can work around this issue by only loading .ckpt checkpoint files from trusted sources and preferring trusted model sources and safer formats such as .safetensors where possible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47747.json
- https://github.com/leejet/stable-diffusion.cpp/security/advisories/GHSA-mghm-5mqc-pwmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47747
- https://github.com/leejet/stable-diffusion.cpp/commit/0a7ae07f948eff4611968a65a22bd7c7031ad74f
- https://github.com/leejet/stable-diffusion.cpp/pull/1443

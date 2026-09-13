# [H] mackron / dr_libs dr_wav.h Heap Buffer Overflow via WAV File

## Summary
Severity: High
Advisory: CVE-2026-29022
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-29022
Type: osv

## Details
dr_libs dr_wav.h version 0.14.4 and earlier (fixed in commit 8a7258c) contain a heap buffer overflow vulnerability in the drwav__read_smpl_to_metadata_obj() function of dr_wav.h that allows memory corruption via crafted WAV files. Attackers can exploit a mismatch between sampleLoopCount validation in pass 1 and unconditional processing in pass 2 to overflow heap allocations with 36 bytes of attacker-controlled data through any drwav_init_*_with_metadata() call on untrusted input.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29022.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29022
- https://www.vulncheck.com/advisories/mackron-dr-libs-heap-buffer-overflow-via-wav-file
- https://github.com/mackron/dr_libs/issues/296
- https://github.com/mackron/dr_libs/commit/8a7258cc66b49387ad58cc5b81568982a3560d49
- https://github.com/mackron/dr_libs
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2026-001-dr-libs-heap-overflow.md

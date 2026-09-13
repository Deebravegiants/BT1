# [C] KissFFT Integer Overflow Heap Buffer Overflow via kiss_fftndr_alloc()

## Summary
Severity: Critical
Advisory: CVE-2026-41445
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-41445
Type: osv

## Details
KissFFT before commit 8a8e66e contains an integer overflow vulnerability in the kiss_fftndr_alloc() function in kiss_fftndr.c where the allocation size calculation dimOther*(dimReal+2)*sizeof(kiss_fft_scalar) overflows signed 32-bit integer arithmetic before being widened to size_t, causing malloc() to allocate an undersized buffer. Attackers can trigger heap buffer overflow by providing crafted dimensions that cause the multiplication to exceed INT_MAX, allowing writes beyond the allocated buffer region when kiss_fftndr() processes the data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41445
- https://www.vulncheck.com/advisories/kissfft-integer-overflow-heap-buffer-overflow-via-kiss-fftndr-alloc
- https://github.com/mborgerding/kissfft/commit/8a8e66e33d692bad1376fe7904d87d767730537f
- https://github.com/mborgerding/kissfft

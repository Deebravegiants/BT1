# [C] KissFFT Integer Overflow Heap Buffer Overflow via kiss_fft_alloc

## Summary
Severity: Critical
Advisory: CVE-2025-34297
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/CVE-2025-34297
Type: osv

## Details
KissFFT versions prior to the fix commit 1b083165 contain an integer overflow in kiss_fft_alloc() in kiss_fft.c on platforms where size_t is 32-bit. The nfft parameter is not validated before being used in a size calculation (sizeof(kiss_fft_cpx) * (nfft - 1)), which can wrap to a small value when nfft is large. As a result, malloc() allocates an undersized buffer and the subsequent twiddle-factor initialization loop writes nfft elements, causing a heap buffer overflow. This vulnerability only affects 32-bit architectures.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34297.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34297
- https://www.vulncheck.com/advisories/kissfft-integer-overflow-heap-buffer-overflow
- https://github.com/mborgerding/kissfft/issues/120
- https://github.com/mborgerding/kissfft/commit/1b08316582049c3716154caefc0deab8758506e3
- https://github.com/mborgerding/kissfft

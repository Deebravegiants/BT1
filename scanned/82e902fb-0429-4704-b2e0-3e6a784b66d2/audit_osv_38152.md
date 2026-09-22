# [C] barebox EFI PE Loader Memory Safety Vulnerabilities

## Summary
Severity: Critical
Advisory: CVE-2026-34963
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-34963
Type: osv

## Details
barebox version prior to 2026.04.0 contains multiple memory-safety vulnerabilities in the EFI PE loader in efi/loader/pe.c where integer overflow in virtual image size computation using 32-bit arithmetic on section VirtualAddress and size values allows undersized heap allocation, and PE section loading logic fails to validate that PointerToRawData plus copied size remains within the PE file buffer. An attacker can supply a malicious EFI PE binary via TFTP, USB, SD card, or network boot to trigger heap buffer overflow or out-of-bounds read from heap memory, potentially achieving code execution in bootloader context.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34963.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34963
- https://www.vulncheck.com/advisories/barebox-efi-pe-loader-memory-safety-vulnerabilities
- https://github.com/barebox/barebox/releases/tag/v2026.04.0
- https://github.com/barebox/barebox
- https://y637f9qq2x.com/posts/barebox-sandbox-vulns/

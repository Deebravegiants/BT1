# [M] libusb < 1.0.30 NULL Pointer Dereference in parse_interface()

## Summary
Severity: Medium
Advisory: CVE-2026-23679
Aliases: PYSEC-2026-3978
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-23679
Type: osv

## Details
libusb before version 1.0.30 contains a NULL pointer dereference vulnerability that allows attackers to crash applications by supplying a malformed USB configuration descriptor where an interface claims bNumEndpoints greater than zero but is followed by a class-specific descriptor whose bLength exceeds the remaining buffer size, causing parse_interface() to return early without allocating the endpoint array. Attackers can exploit this flaw through libusb_get_active_config_descriptor or libusb_get_config_descriptor by providing crafted descriptors via virtualized USB passthrough, file-based descriptor parsing, or network sources, causing any application iterating over endpoints to dereference a NULL endpoint pointer and crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23679.json
- https://github.com/libusb/libusb/releases/tag/v1.0.30
- https://nvd.nist.gov/vuln/detail/CVE-2026-23679
- https://www.vulncheck.com/advisories/libusb-null-pointer-dereference-in-parse-interface
- https://github.com/libusb/libusb/issues/1813
- https://github.com/libusb/libusb/pull/1814
- https://github.com/libusb/libusb/commit/578ab76b4c434f8b204137ab6d7310689c7a9704
- https://github.com/libusb/libusb

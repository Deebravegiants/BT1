# [M] libusb before version 1.0.30 contains a one-byte out-of-bounds read vulnerability in...

## Summary
Severity: Medium
Advisory: JLSEC-2026-666
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-666
Type: osv

## Affected
- Julia: `libusb_jll` — affected >=0 <1.0.30+0

## Details
libusb before version 1.0.30 contains a one-byte out-of-bounds read vulnerability in `parse_iad_array()` in descriptor.c that allows attackers to trigger a denial of service by supplying a malformed USB descriptor whose bLength equals size minus one, causing the bounds check to use the original buffer size instead of the remaining size. Attackers in virtualized environments with USB passthrough can supply crafted descriptors through `libusb_get_active_interface_association_descriptors` or `libusb_get_interface_association_descriptors` to read one byte past the end of the malloc allocation, resulting in a denial of service.

## References
- https://github.com/advisories/GHSA-fh6g-r8pf-wqgw
- https://github.com/libusb/libusb/commit/578ab76b4c434f8b204137ab6d7310689c7a9704
- https://github.com/libusb/libusb/issues/1813
- https://github.com/libusb/libusb/pull/1814
- https://github.com/libusb/libusb/releases/tag/v1.0.30
- https://nvd.nist.gov/vuln/detail/CVE-2026-47104
- https://www.vulncheck.com/advisories/libusb-out-of-bounds-read-in-parse-iad-array

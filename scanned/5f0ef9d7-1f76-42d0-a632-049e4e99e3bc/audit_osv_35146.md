# [M] espressif/usb_host_hid Double-Free Race Condition in USB Host HID Device Close Path

## Summary
Severity: Medium
Advisory: CVE-2025-68657
Aliases: GHSA-gp8r-qjfr-gqfv
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-68657
Type: osv

## Details
Espressif ESP-IDF USB Host HID (Human Interface Device) Driver allows access to HID devices. Prior to 1.1.0, calls to hid_host_device_close() can free the same usb_transfer_t twice. The USB event callback and user code share the hid_iface_t state without locking, so both can tear down a READY interface simultaneously, corrupting heap metadata inside the ESP USB host stack. This vulnerability is fixed in 1.1.0.

## References
- https://components.espressif.com/components/espressif/usb_host_hid/versions/1.1.0/changelog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68657.json
- https://github.com/espressif/esp-usb/security/advisories/GHSA-gp8r-qjfr-gqfv
- https://nvd.nist.gov/vuln/detail/CVE-2025-68657
- https://github.com/espressif/esp-usb/commit/cd28106e9f72ac2719682c06f94601f9f034390b

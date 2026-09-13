# [M] Espressif ESP-IDF USB Host HID (Human Interface Device) Driver Descriptor Use-After-Free Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-68656
Aliases: GHSA-2pm2-62mr-c9x7
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-68656
Type: osv

## Details
Espressif ESP-IDF USB Host HID (Human Interface Device) Driver allows access to HID devices. Prior to 1.1.0, usb_class_request_get_descriptor() frees and reallocates hid_device->ctrl_xfer when an oversized descriptor is requested but continues to use the stale local pointer, leading to an immediate use-after-free when processing attacker-controlled Report Descriptor lengths. This vulnerability is fixed in 1.1.0.

## References
- https://components.espressif.com/components/espressif/usb_host_hid/versions/1.1.0/changelog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68656.json
- https://github.com/espressif/esp-usb/security/advisories/GHSA-2pm2-62mr-c9x7
- https://nvd.nist.gov/vuln/detail/CVE-2025-68656
- https://github.com/espressif/esp-usb/commit/81b37c96593c0bec92ef14c6ee6bf8cab8d8f660

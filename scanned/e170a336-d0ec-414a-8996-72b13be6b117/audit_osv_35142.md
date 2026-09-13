# [M] Espressif ESP-IDF USB Host UVC Class Driver has a stack buffer overflow in UVC descriptor printing

## Summary
Severity: Medium
Advisory: CVE-2025-68622
Aliases: GHSA-g65h-9ggq-9827
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-68622
Type: osv

## Details
Espressif ESP-IDF USB Host UVC Class Driver allows video streaming from USB cameras. Prior to 2.4.0, a vulnerability in the esp-usb UVC host implementation allows a malicious USB Video Class (UVC) device to trigger a stack buffer overflow during configuration-descriptor parsing. When UVC configuration-descriptor printing is enabled, the host prints detailed descriptor information provided by the connected USB device. A specially crafted UVC descriptor may advertise an excessively large length. Because this value is not validated before being copied into a fixed-size stack buffer, an attacker can overflow the buffer and corrupt memory. This vulnerability is fixed in 2.4.0.

## References
- https://components.espressif.com/components/espressif/usb_host_uvc/versions/2.4.0/changelog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68622.json
- https://github.com/espressif/esp-usb/security/advisories/GHSA-g65h-9ggq-9827
- https://nvd.nist.gov/vuln/detail/CVE-2025-68622
- https://github.com/espressif/esp-usb/commit/77a38b15a17f6e3c7aeb620eb4aeaf61d5194cc0

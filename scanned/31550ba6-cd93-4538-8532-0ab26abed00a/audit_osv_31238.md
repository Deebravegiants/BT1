# [M] CVE-2024-6564

## Summary
Severity: Medium
Advisory: CVE-2024-6564
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-6564
Type: osv

## Details
Buffer overflow in "rcar_dev_init"  due to using due to using untrusted data (rcar_image_number) as a loop counter before verifying it against RCAR_MAX_BL3X_IMAGE. This could lead to a full bypass of secure boot.

## References
- https://asrg.io/security-advisories/cve-2024-6564/
- https://github.com/renesas-rcar/arm-trusted-firmware/commit/c9fb3558410032d2660c7f3b7d4b87dec09fe2f2

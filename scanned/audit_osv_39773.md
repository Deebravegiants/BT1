# [H] pam_usb: OTP pad authentication bypass via missing system pad check and uninitialized RNG buffer

## Summary
Severity: High
Advisory: CVE-2026-47272
Aliases: GHSA-vx6f-rrqr-j87c
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-47272
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.9.0, the pusb_pad_compare() function in src/pad.c only verified that the user-side pad (~/.pamusb/device.pad) could be read, but did not enforce that the system-side pad (the pad file on the USB device) was also present and readable. If the user-side pad was deleted or unreadable, the function returned a failure that was treated as non-fatal in certain code paths, allowing authentication to succeed without the USB device being verified. A local user can delete their own ~/.pamusb/device.pad to remove the USB device requirement and authenticate without the physical device. This vulnerability is fixed in 0.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47272.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-vx6f-rrqr-j87c
- https://nvd.nist.gov/vuln/detail/CVE-2026-47272

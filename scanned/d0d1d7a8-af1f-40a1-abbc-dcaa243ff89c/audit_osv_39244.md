# [M] pam_usb: NULL pointer dereference from UDisks device fields causes PAM crash and login denial-of-service

## Summary
Severity: Medium
Advisory: CVE-2026-44710
Aliases: GHSA-j8cq-2gv6-gfwf
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44710
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. Prior to 0.8.7, src/device.c passed the return values of udisks_drive_get_serial(), udisks_drive_get_vendor(), and udisks_drive_get_model() directly to strcmp() without NULL checks. The GIO/UDisks API documentation states these accessors can return NULL for devices that do not expose the corresponding field. Passing NULL to strcmp() is undefined behaviour (typically a SIGSEGV). This vulnerability is fixed in 0.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44710.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-j8cq-2gv6-gfwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44710

# [M] pam_usb: Missing O_EXCL on pad temp file creation allows concurrent update race

## Summary
Severity: Medium
Advisory: CVE-2026-48982
Aliases: GHSA-hxh6-9574-5vp6
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-48982
Type: osv

## Details
pam_usb provides hardware authentication for Linux using ordinary removable media. In versions prior to 0.9.2, when updating a one-time pad file, a temporary file is created using open() without the O_EXCL flag. Without O_EXCL, the create operation is not atomic: two concurrent processes racing to update the same pad may both succeed in opening the file, with the second write silently overwriting the first. The one-time pad is the core replay-prevention mechanism of pam_usb. A successful race could result in the stored pad value diverging from what either process expected, potentially causing authentication failures or, in a precisely timed attack, creating a window for pad reuse. This issue has been fixed in version 0.9.2.

## References
- https://github.com/mcdope/pam_usb/releases/tag/0.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48982.json
- https://github.com/mcdope/pam_usb/security/advisories/GHSA-hxh6-9574-5vp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48982

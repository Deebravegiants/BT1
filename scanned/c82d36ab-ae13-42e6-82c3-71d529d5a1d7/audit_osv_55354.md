# [M] CVE-2025-3522

## Summary
Severity: Medium
Advisory: CVE-2025-3522
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-3522
Type: osv

## Details
Thunderbird processes the X-Mozilla-External-Attachment-URL header to handle attachments which can be hosted externally. When an email is opened, Thunderbird accesses the specified URL to  determine file size, and navigates to it when the user clicks the attachment. Because the URL is not validated or sanitized, it can reference internal resources like chrome:// or SMB share file:// links, potentially leading to hashed Windows credential leakage and opening the door to more serious security issues. This vulnerability affects Thunderbird < 137.0.2 and Thunderbird < 128.9.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2025-26/
- https://www.mozilla.org/security/advisories/mfsa2025-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1955372

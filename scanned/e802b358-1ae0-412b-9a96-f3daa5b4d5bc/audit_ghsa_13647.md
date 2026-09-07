# [M] TinyMCE XSS vulnerability in notificationManager.open API

## Summary
Severity: Medium
Advisory: GHSA-hgqx-r2hp-jr38
CVE: CVE-2023-45819
CWE: CWE-79
Ecosystem: NuGet, Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-hgqx-r2hp-jr38
Type: github-advisory

## Affected
- npm: `tinymce` — affected >=6.0.0 <6.7.1
- NuGet: `TinyMCE` — affected >=6.0.0 <6.7.1
- Packagist: `tinymce/tinymce` — affected >=6.0.0 <6.7.1
- npm: `tinymce` — affected >=0 <5.10.8
- NuGet: `TinyMCE` — affected >=0 <5.10.8
- Packagist: `tinymce/tinymce` — affected >=0 <5.10.8

## Details
### Impact
A [cross-site scripting (XSS)](https://owasp.org/www-community/attacks/xss/) vulnerability was discovered in TinyMCE’s Notification Manager API. The vulnerability exploits TinyMCE's unfiltered notification system, which is used in error handling.  The conditions for this exploit requires carefully crafted malicious content to have been inserted into the editor and a notification to have been triggered.  

When a notification was opened, the HTML within the text argument was displayed unfiltered in the notification. The vulnerability allowed arbitrary JavaScript execution when an notification presented in the TinyMCE UI for the current user.  This issue could also be exploited by any integration which uses a TinyMCE notification to display unfiltered HTML content.

### Patches
This vulnerability has been patched in TinyMCE 5.10.8 and TinyMCE 6.7.1 by ensuring that the HTML displayed in the notification is sanitized, preventing the exploit.

### Fix
To avoid this vulnerability:

* Upgrade to TinyMCE 5.10.8 or higher for TinyMCE 5.x.
* Upgrade to TinyMCE 6.7.1 or higher for TinyMCE 6.x.

### References
* <https://tiny.cloud/docs/release-notes/release-notes5108/#securityfixes>
* <https://tiny.cloud/docs/tinymce/6/6.7.1-release-notes/#security-fixes>

### For more information
If you have any questions or comments about this advisory:
* Email us at <infosec@tiny.cloud>
* Open an issue in the [TinyMCE repo](https://github.com/tinymce/tinymce/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc)

## References
- https://github.com/tinymce/tinymce/security/advisories/GHSA-hgqx-r2hp-jr38
- https://nvd.nist.gov/vuln/detail/CVE-2023-45819
- https://github.com/tinymce/tinymce
- https://tiny.cloud/docs/release-notes/release-notes5108/#securityfixes
- https://tiny.cloud/docs/tinymce/6/6.7.1-release-notes/#security-fixes

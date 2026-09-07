# [M] Cross-site scripting (XSS) in the dynamic file uploads

## Summary
Severity: Medium
Advisory: GHSA-9w99-78rj-hmxq
CVE: CVE-2023-51447
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-9w99-78rj-hmxq
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0.27.0 <0.27.5
- RubyGems: `decidim-core` — affected >=0.27.0 <0.27.5

## Details
### Impact
The dynamic file upload feature is subject to potential XSS attach in case the attacker manages to modify the file names of the records being uploaded to the server.

This appears in sections where the user controls the file upload dialogs themselves and has the technical knowledge to change the file names through the dynamic upload endpoint. Therefore I believe it would require the attacker to control the whole session of the particular user but in any case, this needs to be fixed.

Successful exploit of this vulneratibility would require the user to have successfully uploaded a file blob to the server with a malicious file name and then have the possibility to direct the other user to the edit page of the record where the attachment is attached.

The users are able to craft the direct upload requests themselves controlling the file name that gets stored to the database as shown here:
https://github.com/rails/rails/blob/a967d355c6fee9ad9b8bd115d43bc8b0fc207e7e/activestorage/app/controllers/active_storage/direct_uploads_controller.rb#L14

The attacker is able to change the filename e.g. to `<svg onload=alert('XSS')>` if they know how to craft these requests themselves. And then enter the returned blob ID to the form inputs manually by modifying the edit page source.

Therefore, anywhere we display these strings, we should properly escape them.

### Patches
PR #11612 fixes this problem both for 0.28.dev and 0.27.x.

### Workarounds
Disable dynamic uploads for the instance, e.g. from proposals.

### References
OWASP ASVS v4.0.3-5.1.3

### Credits
This issue was discovered in City of Helsinki's security audit against Decidim 0.27 done during September 2023. The security audit was implemented by [Deloitte Finland](https://www2.deloitte.com/fi/fi.html).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-9w99-78rj-hmxq
- https://nvd.nist.gov/vuln/detail/CVE-2023-51447
- https://github.com/decidim/decidim/pull/11612
- https://github.com/decidim/decidim/commit/aaf72787cf18beeeb6a771c1f7cbb7654b073423
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.27.5
- https://github.com/decidim/decidim/releases/tag/v0.28.0
- https://github.com/rails/rails/blob/a967d355c6fee9ad9b8bd115d43bc8b0fc207e7e/activestorage/app/controllers/active_storage/direct_uploads_controller.rb#L14

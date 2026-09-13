# [H] The same file cannot be opened with different rights

## Summary
Severity: High
Advisory: CVE-2023-46743
Aliases: GHSA-mvq3-xxg2-rj57
CVSS: 7.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-11-09
Source: https://osv.dev/vulnerability/CVE-2023-46743
Type: osv

## Details
application-collabora is an integration of Collabora Online in XWiki. As part of the application use cases, depending on the rights that a user has over a document, they should be able to open the office attachments files in view or edit mode. Currently, if a user opens an attachment file in edit mode in collabora, this right will be preserved for all future users, until the editing session is closes, even if some of them have only view right. Collabora server is the one issuing this request and it seems that the `userCanWrite` query parameter is cached, even if, for example, token is not. This issue has been patched in version 1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46743.json
- https://github.com/xwikisas/application-collabora/security/advisories/GHSA-mvq3-xxg2-rj57
- https://nvd.nist.gov/vuln/detail/CVE-2023-46743

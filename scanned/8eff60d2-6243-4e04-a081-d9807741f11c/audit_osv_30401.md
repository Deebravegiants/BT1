# [H] macro-pdfviewer's preview in WYSIWYG editor allows accessing any PDF document as the last author

## Summary
Severity: High
Advisory: CVE-2024-52298
Aliases: GHSA-hph4-7j37-7c97
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/CVE-2024-52298
Type: osv

## Details
macro-pdfviewer is a PDF Viewer Macro for XWiki using Mozilla pdf.js. The PDF Viewer macro allows an attacker to view any attachment using the "Delegate my view right" feature as long as the attacker can view a page whose last author has access to the attachment. For this, the attacker only needs to provide the reference to a PDF file to the macro. To obtain the reference of the desired attachment, the attacker can access the Page Index, Attachments tab. Even if the UI shows N/A, the user can inspect the page and check the HTTP request that fetches the live data entries. The attachment URL is available in the returned JSON for all attachments, including protected ones and allows getting the necessary values. This vulnerability is fixed in version 2.5.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52298.json
- https://github.com/xwikisas/macro-pdfviewer/security/advisories/GHSA-hph4-7j37-7c97
- https://nvd.nist.gov/vuln/detail/CVE-2024-52298

# [M] XML Notepad: XML External Entity (XXE) Injection via Unsafe XmlTextReader in XML Diff and Schema Loading

## Summary
Severity: Medium
Advisory: CVE-2026-34401
Aliases: GHSA-5j32-486h-42ch
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34401
Type: osv

## Details
XML Notepad is a Windows program that provides a simple intuitive User Interface for browsing and editing XML documents. Prior to version 2.9.0.21, XML Notepad does not disable DTD processing by default which means external entities are resolved automatically. There is a well known attack related to malicious DTD files where an attacker to craft a malicious XML file that loads a DTD that causes XML Notepad to make outbound HTTP/SMB requests, potentially leaking local file contents or capturing the victim's NTLM credentials. This issue has been patched in version 2.9.0.21.

## References
- https://github.com/microsoft/XmlNotepad/releases/tag/2.9.0.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34401.json
- https://github.com/microsoft/XmlNotepad/security/advisories/GHSA-5j32-486h-42ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-34401
- https://github.com/microsoft/XmlNotepad/commit/3665603d61ba10b7827a3724e854748cb780140c
- https://github.com/microsoft/XmlNotepad/commit/c03ab2311ac6960452eb1ab49098768f851dcc53

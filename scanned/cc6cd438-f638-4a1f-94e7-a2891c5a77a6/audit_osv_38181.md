# [H] CVE-2026-3511

## Summary
Severity: High
Advisory: CVE-2026-3511
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-3511
Type: osv

## Details
Improper Restriction of XML External Entity Reference vulnerability in XMLUtils.java in Slovensko.Digital Autogram allows remote unauthenticated attacker to conduct SSRF (Server Side Request Forgery) attacks and obtain unauthorized access to local files on filesystems running the vulnerable application. Successful exploitation requires the victim to visit a specially crafted website that sends request containing a specially crafted XML document to /sign endpoint of the local HTTP server run by the application.

## References
- https://github.com/slovensko-digital/autogram/releases/tag/v2.7.2
- https://blog.binary.house/2026/03/pripadova-studia-ako-sme-s-claude-code.html

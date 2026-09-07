# [M] XWiki view file macro: User can view content of office file without view rights on the attachment 

## Summary
Severity: Medium
Advisory: GHSA-8c52-x9w7-vc95
CVE: CVE-2025-65089
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-8c52-x9w7-vc95
Type: github-advisory

## Affected
- Maven: `com.xwiki.pro:xwiki-pro-macros-ui` — affected >=0 <1.27.0

## Details
### Summary
A user with no view rights on a page may see the content of an office attachment displayed with the view file macro.

### Details
If on a public page is displayed an office attachment from a restricted page, a user with no view rights on the restricted page can view the attachment content, no matter the display type used.

### PoC
1. Install and activate the Pro Macros application
2. Create a page and limit the view rights for a test user
3. Add an attachment to the restricted page
4. Create a new public page
5. Add the view file macro and select the attachment from the restricted page using any display type
6. Login as the test user with restricted view rights
7. The user will see the content despite having no view rights

### Workarounds
None

### Impact
Private data can be leaked if a user knows the reference to an attachment and has edit rights on a page.

## References
- https://github.com/xwikisas/xwiki-pro-macros/security/advisories/GHSA-8c52-x9w7-vc95
- https://nvd.nist.gov/vuln/detail/CVE-2025-65089
- https://github.com/xwikisas/xwiki-pro-macros

# [C] CI4MS: Blogs Posts (Categories) Full Account Takeover for All-Roles & Privilege-Escalation via Stored DOM XSS

## Summary
Severity: Critical
Advisory: GHSA-r33w-c82v-x5v7
CVE: CVE-2026-34567
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-r33w-c82v-x5v7
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.0.0

## Details
# Summary  
### **Vulnerability: Blogs Posts (Categories) Full Account Takeover for All-Roles & Privilege-Escalation via Stored DOM XSS**
- Stored Cross-Site Scripting via Unsanitized Blog Post Content in Blog Management (Categories)

### Description
The application fails to properly sanitize user-controlled input when creating or editing blog posts within the **Categories** section. An attacker can inject a malicious JavaScript payload into the **Categories** content, which is then stored server-side.

This stored payload is later rendered unsafely when the **Categories** are viewed via blog posts, without proper output encoding, leading to stored cross-site scripting (XSS).

### Affected Functionality
- Blog post **Categories** creation functionality
- Blog post **Categories** editing functionality
- Blog post **Categories** storage and retrieval logic

### Attack Scenario
- An attacker creates or edits a blog post **Category** to include a malicious XSS payload in the category description or name.
- The application stores this content without sanitization or encoding.
- The payload persists and executes whenever the category is viewed within the blog posts section, leading to the execution of arbitrary JavaScript in the victim’s browser.

### Impact
- Persistent Stored XSS
- Execution of arbitrary JavaScript in victims’ browsers
- Privilege escalation when viewed by administrators or privileged users within the **Categories** functionality
- Full administrator account takeover through **Categories** access
- Full account takeover across all roles via **Categories** pages
- Full compromise of the entire application via XSS in **Categories**

**Endpoints:**
- `/backend/blogs/create` (Categories specific)
- `/backend/blogs/` (Categories view)
- `/blog/{id}` (Rendered blog post under Categories)

## Steps To Reproduce (POC)
1. Go to the **Categories** section of the blog management panel.
2. Create a new category or edit an existing category.
3. Insert an XSS payload into the category content, such as:
`<img src=x onerror=alert(document.domain)>`
4. Save or publish the Categories.
5. View the category via the blog posts in the administrative panel or public blog page under the Categories section.
6. Notice the XSS payload executing automatically when the Category is viewed in the Blog Posts.

## Remediation

- **Avoid unsafe DOM manipulation methods:** Do not use `.html()`, `innerHTML`, or similar sink functions in client-side JavaScript or server-side templating (e.g., PHP). Even when user input flowing into these sinks is not immediately apparent, they can introduce Cross-Site Scripting (XSS) vulnerabilities that an attacker may exploit.

- **Apply output encoding:** Implement HTML entity encoding on all user-controlled data before rendering it in the browser. This helps neutralize potentially malicious input.

- **Implement input sanitization:** Ensure that all user-supplied input is properly sanitized before processing or output. Currently, no sanitization mechanisms are in place, which should be addressed as a priority.

- **Enforce security headers and cookie attributes:**
  - **Content Security Policy (CSP):** Define and enforce a strict CSP to limit the execution of unauthorized scripts.
  - **HttpOnly flag:** Set the `HttpOnly` attribute on session cookies to prevent client-side script access.
  - **SameSite attribute:** Configure the `SameSite` cookie attribute to mitigate Cross-Site Request Forgery (CSRF) risks.
  - **Secure flag:** Ensure all cookies are transmitted only over HTTPS by enabling the `Secure` attribute.

  These measures collectively reduce the impact of XSS and help prevent escalation paths such as CSRF via XSS.

# Ready Video POC:
https://mega.nz/file/SAdVxK7b#kFW_sFOim_d_1AnVcpwvzOEV4MHv33LLooL4Xa_Ymgg

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-r33w-c82v-x5v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-34567
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.0.0

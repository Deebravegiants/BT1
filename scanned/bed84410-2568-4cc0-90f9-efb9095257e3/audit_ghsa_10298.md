# [C] CI4MS: System Settings (Social Media Management) Full Platform Compromise & Full Account Takeover for All-Roles & Privilege-Escalation via Stored DOM XSS

## Summary
Severity: Critical
Advisory: GHSA-gcfj-cf7j-vwgj
CVE: CVE-2026-34561
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-gcfj-cf7j-vwgj
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.0.0

## Details
## Summary
### **Vulnerability: Stored DOM XSS via System Settings – Social Media Management (Same-Page Attribute Breakout & Persistent Payload Injection)**
- Stored Cross-site Scripting via Unsanitized Social Media Configuration Fields with Immediate Same-Page Execution

### Description
The application fails to properly sanitize user-controlled input within **System Settings – Social Media Management**. Multiple configuration fields, including **Social Media** and **Social Media Link**, accept attacker-controlled input that is stored server-side and later rendered without proper output encoding.

Unlike typical stored XSS that executes on other pages (such as public-facing landing pages), this vulnerability executes directly on the same settings page. The injected payload breaks out of the input attribute context and is immediately interpreted by the browser, resulting in same-page DOM-based XSS.

This represents a different functionality and a separate vulnerability class from public-facing landing page injection.

### Affected Functionality
- System Settings – Social Media Management configuration
- Same-page rendering of user-controlled input fields
- DOM attribute injection within form inputs
- Storage and retrieval of social media configuration values

### Attack Scenario
- An attacker injects a malicious JavaScript payload into one or more Social Media Management fields.
- The payload breaks out of the HTML attribute context.
- The application stores and re-renders the payload without sanitization or encoding.
- The payload executes immediately on the same settings page when rendered.
- The script executes in the browser context of the authenticated user managing settings.

### Impact
- Persistent Stored XSS
- Immediate Same-Page DOM XSS execution
- Execution of arbitrary JavaScript in victims’ browsers
- Administrative privilege escalation
- Full administrator account takeover
- Full account takeover across all roles
- Full compromise of the entire platform

Endpoints:
- `/backend/settings/` (Social Media Management)

## Steps To Reproduce (POC)
1. Navigate to System Settings -> Social Media Management
2. Insert the following XSS payload into any Social Media or Social Media Link field:
`test"><img src=1 onerror=alert()>" class="form-control" placeholder="Name" required>`
3. Save the settings
4. Observe that the payload breaks out of the input attribute context
5. The XSS executes immediately on the same page

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
https://mega.nz/file/PBEFBCpJ#rGGxjnPN38qDtmJssAgIoLuStBcQaZFpR0J1bKAXApc

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-gcfj-cf7j-vwgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34561
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.0.0

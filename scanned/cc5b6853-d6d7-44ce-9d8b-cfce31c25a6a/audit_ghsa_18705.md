# [H] Better Auth: Unauthenticated API key creation through api-key plugin

## Summary
Severity: High
Advisory: GHSA-99h5-pjcv-gr6v
CVE: CVE-2025-61928
CWE: CWE-285, CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-99h5-pjcv-gr6v
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.3.26

## Details
### **Summary**

A critical authentication bypass was identified in the API key creation and update endpoints. An attacker could create or modify API keys for arbitrary users by supplying a victim’s user ID in the request body. Due to a flaw in how the authenticated user was derived, the endpoints could treat attacker-controlled input as an authenticated user object under certain conditions.

### **Details**

The vulnerability originated from fallback logic used when determining the current user. When no session was present, the handler incorrectly allowed request-body data to populate the user context used for authorization decisions. Because server-side validation only executed when authentication was required, privileged fields were not properly protected. As a result, the API accepted unauthenticated requests that targeted other users.

This same pattern affected both the API key creation and update routes.

### **Impact**

Unauthenticated attackers could generate or modify API keys belonging to any user. This granted full authenticated access as the targeted user and, depending on the user’s privileges, could lead to account compromise, access to sensitive data, or broader application takeover.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-99h5-pjcv-gr6v
- https://nvd.nist.gov/vuln/detail/CVE-2025-61928
- https://github.com/better-auth/better-auth/commit/556085067609c508f8c546ceef9003ee8c607d39
- https://github.com/better-auth/better-auth

# [H] RedwoodSDK has a CSRF vulnerability in server function dispatch via GET requests

## Summary
Severity: High
Advisory: GHSA-x8rx-789c-2pxq
CVE: CVE-2026-39371
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-x8rx-789c-2pxq
Type: github-advisory

## Affected
- npm: `rwsdk` — affected >=1.0.0-beta.50 <1.0.6

## Details
**Summary**

Server functions exported from `"use server"` files could be invoked via GET requests, bypassing their intended HTTP method. In cookie-authenticated applications, this allowed cross-site GET navigations to trigger state-changing functions, because browsers send `SameSite=Lax` cookies on top-level GET requests.

This affected all server functions -- both `serverAction()` handlers and bare exported functions in `"use server"` files.

**Impact**

An attacker could construct a URL containing a known action ID and JSON-encoded arguments. When a victim with an active session visited or was redirected to this URL, the function executed with the victim's credentials. This affected any server function that performs state-changing operations (writes, deletes, mutations) in applications using cookie-based authentication.

**Remediation**

Update to rwsdk `1.0.6`. No application code changes are required.

The fix enforces the declared HTTP method at dispatch time. GET requests to server functions that require POST now return `405 Method Not Allowed`.

## References
- https://github.com/redwoodjs/sdk/security/advisories/GHSA-x8rx-789c-2pxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-39371
- https://github.com/redwoodjs/sdk

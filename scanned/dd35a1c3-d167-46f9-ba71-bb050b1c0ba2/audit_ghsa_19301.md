# [M] nosurf vulnerable to CSRF due to non-functional same-origin request checks

## Summary
Severity: Medium
Advisory: GHSA-w9hf-35q4-vcjw
CVE: CVE-2025-46721
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-w9hf-35q4-vcjw
Type: github-advisory

## Affected
- Go: `github.com/justinas/nosurf` — affected >=0 <1.2.0

## Details
### Impact

This vulnerability allows an attacker who controls content on the target site, or on a subdomain of the target site (either via XSS, or otherwise) to bypass Cross-Site Request Forgery checks and issue requests on user's behalf.

### Details

Due to misuse of the Go `net/http` library, nosurf categorizes all incoming requests as plain-text HTTP requests, in which case the `Referer` header is not checked to have the same origin as the target webpage.

If the attacker has control over HTML contents on either the target website (e.g. `example.com`), or on a website hosted on a subdomain of the target (e.g. `attacker.example.com`), they will also be able to manipulate cookies set for the target website. By acquiring the secret CSRF token from the cookie, or overriding the cookie with a new token known to the attacker, `attacker.example.com` is able to craft cross-site requests to `example.com`. 

### Patches

A patch for the issue was released in nosurf 1.2.0.

### Workarounds

In lieu of upgrading to a patched version of nosurf, users may additionally use another HTTP middleware to ensure that a non-safe HTTP request is coming from the same origin (e.g. by requiring a `Sec-Fetch-Site: same-origin` header in the request).

### References

https://github.com/advisories/GHSA-rq77-p4h8-4crw
https://github.com/justinas/nosurf-cve-2025-46721
https://www.cve.org/CVERecord?id=CVE-2025-46721
https://github.com/justinas/nosurf/releases/tag/v1.2.0

## References
- https://github.com/justinas/nosurf/security/advisories/GHSA-w9hf-35q4-vcjw
- https://nvd.nist.gov/vuln/detail/CVE-2025-46721
- https://github.com/justinas/nosurf/commit/ec9bb776d8e5ba9e906b6eb70428f4e7b009feee
- https://github.com/advisories/GHSA-rq77-p4h8-4crw
- https://github.com/justinas/nosurf
- https://github.com/justinas/nosurf-cve-2025-46721
- https://github.com/justinas/nosurf/releases/tag/v1.2.0

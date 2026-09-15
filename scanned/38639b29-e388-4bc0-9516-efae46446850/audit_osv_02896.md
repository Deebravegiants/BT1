# [M] ALPINE-CVE-2023-45803

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-45803
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.2 (CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-45803
Type: osv

## Affected
- Alpine:v3.15: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.16: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.17: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.18: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.19: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.20: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.21: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.22: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.23: `py3-urllib3` — affected >=0 <1.26.18-r0
- Alpine:v3.24: `py3-urllib3` — affected >=0 <1.26.18-r0

## Details
urllib3 is a user-friendly HTTP client library for Python. urllib3 previously wouldn't remove the HTTP request body when an HTTP redirect response using status 301, 302, or 303 after the request had its method changed from one that could accept a request body (like `POST`) to `GET` as is required by HTTP RFCs. Although this behavior is not specified in the section for redirects, it can be inferred by piecing together information from different sections and we have observed the behavior in other major HTTP client implementations like curl and web browsers. Because the vulnerability requires a previously trusted service to become compromised in order to have an impact on confidentiality we believe the exploitability of this vulnerability is low. Additionally, many users aren't putting sensitive data in HTTP request bodies, if this is the case then this vulnerability isn't exploitable. Both of the following conditions must be true to be affected by this vulnerability: 1. Using urllib3 and submitting sensitive information in the HTTP request body (such as form data or JSON) and 2. The origin service is compromised and starts redirecting using 301, 302, or 303 to a malicious peer or the redirected-to service becomes compromised. This issue has been addressed in versions 1.26.18 and 2.0.7 and users are advised to update to resolve this issue. Users unable to update should disable redirects for services that aren't expecting to respond with redirects with `redirects=False` and disable automatic redirects with `redirects=False` and handle 301, 302, and 303 redirects manually by stripping the HTTP request body.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-45803

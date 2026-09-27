# [C] Lightpanda: fetch() and XMLHttpRequest attach session cookies to cross-origin requests regardless of credentials mode

## Summary
Severity: Critical
Advisory: CVE-2026-52843
Aliases: GHSA-36mm-v3c2-24cc
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52843
Type: osv

## Details
Lightpanda is a headless browser designed for AI and automation. Prior to 0.2.9, Lightpanda fetch() and XMLHttpRequest unconditionally attached session cookies to every HTTP request, ignoring credentials: omit, credentials: same-origin, credentials: include, and XMLHttpRequest.withCredentials, allowing an attacker-controlled origin in a Lightpanda session to issue authenticated cross-origin requests against a victim origin. This issue is fixed in version 0.2.9.

## References
- https://github.com/lightpanda-io/browser/releases/tag/0.2.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52843.json
- https://github.com/lightpanda-io/browser/security/advisories/GHSA-36mm-v3c2-24cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-52843
- https://github.com/lightpanda-io/browser/commit/2cdaac780bed65db98bbb6ed2ad5bc6011863c76
- https://github.com/lightpanda-io/browser/pull/2155

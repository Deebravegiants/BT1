# [H] Pinry Pinry - Server-Side Request Forgery

## Summary
Severity: High
Advisory: CVE-2026-72606
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72606
Type: osv

## Details
A server-side request forgery vulnerability in Pinry through 2.1.13 allows unauthenticated remote attackers to make the server issue HTTP requests to arbitrary internal or external hosts via the pin-from-URL feature. The feature passes the user-supplied URL directly to requests.get() without host or IP validation, and ALLOW_NEW_REGISTRATIONS defaults to true enabling anonymous triggering. An attacker can reach internal services or cloud metadata endpoints from the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72606.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72606
- https://github.com/pinry/pinry

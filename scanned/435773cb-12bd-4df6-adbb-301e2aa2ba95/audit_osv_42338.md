# [M] Perspective 5.0.0 DoS via Loop Expression Evaluation

## Summary
Severity: Medium
Advisory: CVE-2026-67199
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-67199
Type: osv

## Details
Perspective 5.0.0 contains a denial of service vulnerability that allows remote attackers to block the server event loop indefinitely by submitting a crafted expression containing unbounded for or while loop constructs in a TableMakeViewReq message. Attackers can embed an arbitrarily large iteration count in an expression column evaluated once per table row, causing the Tornado IOLoop to block without any iteration cap, deadline, or cancellation check, rendering the server unresponsive to all connected clients.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67199
- https://www.vulncheck.com/advisories/perspective-dos-via-loop-expression-evaluation
- https://github.com/perspective-dev/perspective
- https://christbowel.com/blog/perspective-5-0-0-five-cves/

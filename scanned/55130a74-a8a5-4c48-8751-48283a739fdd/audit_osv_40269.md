# [C] Lightpanda:URL parser misidentifies page origin for URLs containing @ in the path - Same-Origin Policy bypass

## Summary
Severity: Critical
Advisory: CVE-2026-52842
Aliases: GHSA-mq6p-m9cc-q432
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52842
Type: osv

## Details
Lightpanda is a headless browser designed for AI and automation. Prior to 0.3.1, Lightpanda searched for @ across the entire URL string instead of only the authority component when computing a page origin, so a URL such as `http://attacker.com/@victim.com/` was fetched from attacker.com but treated as `http://victim.com`, allowing a complete Same-Origin Policy bypass. This issue is fixed in version 0.3.1.

## References
- https://github.com/lightpanda-io/browser/releases/tag/0.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52842.json
- https://github.com/lightpanda-io/browser/security/advisories/GHSA-mq6p-m9cc-q432
- https://nvd.nist.gov/vuln/detail/CVE-2026-52842
- https://github.com/lightpanda-io/browser/commit/0588cc374d4af9687cf6f45a7d52f7af04bbacfb
- https://github.com/lightpanda-io/browser/pull/1998

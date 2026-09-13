# [M] WWBN AVideo: Exposure of Sensitive Information to an Unauthorized Actor and Missing Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-43885
Aliases: GHSA-xr49-f4rh-qcjf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43885
Type: osv

## Details
WWBN AVideo is an open source video platform. In versions up to and including 29.0, an unauthenticated user can read APISecret from objects/plugins.json.php and use it to call protected API endpoints (e.g. users_list) without logging in. Commit 1c36f229d0a103528fb9f64d0a1cc0e1e8f5999b contains an updated fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43885.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xr49-f4rh-qcjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-43885
- https://github.com/WWBN/AVideo/commit/1c36f229d0a103528fb9f64d0a1cc0e1e8f5999b

# [M] CVE-2025-66803

## Summary
Severity: Medium
Advisory: CVE-2025-66803
Aliases: GHSA-qppm-g56g-fpvp
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-66803
Type: osv

## Details
Race condition in the turbo-frame element handler in Hotwired Turbo before 8.0.x causes logout operations to fail when delayed frame responses reapply session cookies after logout. This can be exploited by remote attackers via selective network delays (e.g. delaying requests based on sequence or timing) or by physically proximate attackers when the race condition occurs naturally on shared computers.

## References
- https://turbo.hotwired.dev/handbook/frames
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66803.json
- https://github.com/hotwired/turbo/security/advisories/GHSA-qppm-g56g-fpvp
- https://nvd.nist.gov/vuln/detail/CVE-2025-66803
- https://github.com/hotwired/turbo/pull/1399

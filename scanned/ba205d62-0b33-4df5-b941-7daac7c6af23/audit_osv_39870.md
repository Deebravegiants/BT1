# [M] Kolibri has Unauthenticated Server-Side Request Forgery (SSRF) in RemoteFacilityUserViewset

## Summary
Severity: Medium
Advisory: CVE-2026-48053
Aliases: GHSA-4mj9-pf4r-cqrc, PYSEC-2026-2554
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-48053
Type: osv

## Details
Kolibri is an offline-first education platform. Prior to version 0.19.4, several Kolibri API endpoints accept an unvalidated `baseurl` parameter and fetch attacker-controlled URLs from the Kolibri server, reflecting the response body back to the caller. The original report identified two endpoints on the `RemoteFacilityUser*` viewsets; remediation review found two further reflection points on the same pattern. The GET endpoint was unauthenticated. Version 0.19.4 fixes the vulnerability.

## References
- https://github.com/learningequality/kolibri/releases/tag/v0.19.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48053.json
- https://github.com/learningequality/kolibri/security/advisories/GHSA-4mj9-pf4r-cqrc
- https://github.com/pypa/advisory-database/tree/main/vulns/kolibri/PYSEC-2026-2554.yaml
- https://nvd.nist.gov/vuln/detail/CVE-2026-48053

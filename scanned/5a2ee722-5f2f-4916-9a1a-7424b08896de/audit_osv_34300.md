# [M] Improper header parsing may lead to request smuggling

## Summary
Severity: Medium
Advisory: CVE-2025-57783
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2025-57783
Type: osv

## Details
Improper header parsing may lead to request smuggling has been identified in Hiawatha webserver version 11.7 which allows an unauthenticated attacker to access restricted resources managed by Hiawatha webserver.

## References
- https://gitlab.com/hsleisink/hiawatha/-/blame/master/src/http.c?ref_type=heads#L205
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57783.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57783

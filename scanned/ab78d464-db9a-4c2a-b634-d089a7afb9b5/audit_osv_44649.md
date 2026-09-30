# [M] UnoPim before 2.1.3 Missing Authorization on Integration Management Routes

## Summary
Severity: Medium
Advisory: CVE-2026-85395
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85395
Type: osv

## Details
UnoPim before 2.1.3 fails to include integration store, update, and key-generation routes in its ACL map, allowing any admin user to bypass permission checks. Attackers with minimal admin privileges can create OAuth API integrations, mint client credentials, and escalate permissions by exploiting missing authorization validation in the Bouncer middleware.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85395.json
- https://github.com/unopim/unopim/releases/tag/v2.1.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-85395
- https://www.vulncheck.com/advisories/unopim-before-2.1.3-missing-authorization-on-integration-management-routes
- https://github.com/unopim/unopim/commit/acbf2e160ced78446d6e4267e89f264bf04612c4
- https://github.com/unopim/unopim
- https://github.com/geo-chen/oss/blob/main/unopim.md
- https://github.com/unopim/unopim/blob/v2.1.2/packages/Webkul/User/src/Http/Middleware/Bouncer.php

# [C] CVE-2025-56643

## Summary
Severity: Critical
Advisory: CVE-2025-56643
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-56643
Type: osv

## Details
Requarks Wiki.js 2.5.307 does not properly revoke or invalidate active JWT tokens when a user logs out. As a result, previously issued tokens remain valid and can be reused to access the system, even after logout. This behavior affects session integrity and may allow unauthorized access if a token is compromised. The issue is present in the authentication resolver logic and affects both the GraphQL endpoint and the logout mechanism.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56643.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56643
- https://github.com/0xBS0D27/CVE-2025-56643

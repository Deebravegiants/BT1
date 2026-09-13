# [C] CVE-2026-31272

## Summary
Severity: Critical
Advisory: CVE-2026-31272
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-31272
Type: osv

## Details
MRCMS 3.1.2 contains an access control vulnerability. The save() method in src/main/java/org/marker/mushroom/controller/UserController.java lacks proper authorization validation, enabling direct addition of super administrator accounts without authentication.

## References
- https://github.com/clockw1se0v0/Vul/blob/main/MRCMS/Unauthorized.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31272.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31272

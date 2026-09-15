# [M] iTop missing silo check on extkey in console and portal

## Summary
Severity: Medium
Advisory: CVE-2023-45808
Aliases: GHSA-245j-66p9-pwmh
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2024-04-15
Source: https://osv.dev/vulnerability/CVE-2023-45808
Type: osv

## Details
iTop is an IT service management platform.  When creating or updating an object, extkey values aren't checked to be in the current user silo. In other words, by forging an http request, the user can create objects pointing to out of silo objects (for example a UserRequest in an out of scope Organization). Fixed in iTop 2.7.10, 3.0.4, 3.1.1, and 3.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45808.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-245j-66p9-pwmh
- https://nvd.nist.gov/vuln/detail/CVE-2023-45808
- https://github.com/Combodo/iTop/commit/5a434486443a2cf8b8a288475aada54d0a068ca7
- https://github.com/Combodo/iTop/commit/8f61c02cbe17badff87bff9b8ada85e783c47385

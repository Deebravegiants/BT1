# [C] Emby Server allows attackers to gain administrative server access without preconditions

## Summary
Severity: Critical
Advisory: CVE-2025-64113
Aliases: GHSA-95fv-5gfj-2r84
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-64113
Type: osv

## Details
Emby Server is a user-installable home media server. Versions below 4.9.1.81 allow an attacker to gain full administrative access to an Emby Server (for Emby Server administration, not at the OS level). Other than network access, no specific preconditions need to be fulfilled for a server to be vulnerable. This issue is fixed in version 4.9.1.81.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64113.json
- https://github.com/EmbySupport/Emby.Security/security/advisories/GHSA-95fv-5gfj-2r84
- https://nvd.nist.gov/vuln/detail/CVE-2025-64113

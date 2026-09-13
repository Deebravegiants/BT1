# [H] FreshRSS has Incomplete Session Termination on Logout

## Summary
Severity: High
Advisory: CVE-2025-54592
Aliases: GHSA-42v4-65f8-5wgr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-54592
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. Versions 1.26.3 and below do not properly terminate the session during logout. After a user logs out, the session cookie remains active and unchanged. The unchanged cookie could be reused by an attacker if a new session were to be started. This failure to invalidate the session can lead to session hijacking and fixation vulnerabilities. This issue is fixed in version 1.27.0

## References
- https://github.com/FreshRSS/FreshRSS/releases/tag/1.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54592.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-42v4-65f8-5wgr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54592
- https://github.com/FreshRSS/FreshRSS/pull/7762

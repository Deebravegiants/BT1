# [H] FreshRSS: Unauthenticated users can view default user's  information

## Summary
Severity: High
Advisory: CVE-2025-54591
Aliases: GHSA-jf4v-f8p2-8xvq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-54591
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. Versions 1.26.3 and below expose information about feeds and tags of default admin users, due to lack of access checking in the FreshRSS_Auth::hasAccess() function used by some of the tag/feed related endpoints. FreshRSS controllers usually have a defined firstAction() method with an override to make sure that every action requires access. If one doesn't, then every action has to check for access manually, and certain endpoints use neither the firstAction() method, or do they perform a manual access check. This issue is fixed in version 1.27.0.

## References
- https://github.com/FreshRSS/FreshRSS/releases/tag/1.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54591.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-jf4v-f8p2-8xvq
- https://nvd.nist.gov/vuln/detail/CVE-2025-54591
- https://github.com/FreshRSS/FreshRSS/pull/7768

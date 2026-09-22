# [H] NamelessMC Has Forum Reply Submission Time Limit Bypass

## Summary
Severity: High
Advisory: CVE-2025-31118
Aliases: GHSA-jhvp-mwj4-922m
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-31118
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. In version 2.1.4 and prior, forum quick reply feature (view_topic.php) does not implement any spam prevention mechanism. This allows authenticated users to continuously post replies without any time restriction, resulting in an uncontrolled surge of posts that can disrupt normal operations. This issue has been patched in version 2.2.0.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31118.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-jhvp-mwj4-922m
- https://nvd.nist.gov/vuln/detail/CVE-2025-31118
- https://github.com/NamelessMC/Nameless/commit/51e9d93aaa28d40f060b807533d22b768abea207

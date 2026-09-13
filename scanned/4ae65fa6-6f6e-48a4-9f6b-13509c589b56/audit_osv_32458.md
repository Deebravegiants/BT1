# [H] NamelessMC Forum Topic Deletion Triggered by Unrelated User Deletion

## Summary
Severity: High
Advisory: CVE-2025-30357
Aliases: GHSA-22mc-7c9m-gv8h
CVSS: 7.3 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:N/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-30357
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. In version 2.1.4 and prior, if a malicious user is leaving spam comments on many topics then an administrator, unable to manually remove each spam comment, may delete the malicious account. Once an administrator deletes the malicious user's account, all their posts (comments) along with the associated topics (by unrelated users) will be marked as deleted. This issue has been patched in version 2.2.0.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30357.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-22mc-7c9m-gv8h
- https://nvd.nist.gov/vuln/detail/CVE-2025-30357
- https://github.com/NamelessMC/Nameless/commit/7040924e27f99aa486c619a5b4ca809051a1ca7f

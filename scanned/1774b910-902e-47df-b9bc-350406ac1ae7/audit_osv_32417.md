# [H] NamelessMC Has Lack of Length Validation for s Parameter in GET Requests

## Summary
Severity: High
Advisory: CVE-2025-29784
Aliases: GHSA-4hrq-rf96-c2jm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-29784
Type: osv

## Details
NamelessMC is a free, easy to use & powerful website software for Minecraft servers. In version 2.1.4 and prior, the s parameter in GET requests for forum search functionality lacks length validation, allowing attackers to submit excessively long search queries. This oversight can lead to performance degradation and potential denial-of-service (DoS) attacks. This issue has been patched in version 2.2.0.

## References
- https://github.com/NamelessMC/Nameless/releases/tag/v2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29784.json
- https://github.com/NamelessMC/Nameless/security/advisories/GHSA-4hrq-rf96-c2jm
- https://nvd.nist.gov/vuln/detail/CVE-2025-29784
- https://github.com/NamelessMC/Nameless/commit/f5341e56930a98978171e0a871d60f19ab30ebdd

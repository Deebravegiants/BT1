# [M] WOWS Karma vulnerable to a post submission bounce/timing attack

## Summary
Severity: Medium
Advisory: CVE-2024-34695
Aliases: GHSA-v6cc-v976-mj8g
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:H)
Published: 2024-05-10
Source: https://osv.dev/vulnerability/CVE-2024-34695
Type: osv

## Details
WOWS Karma is a reputation system for Wargaming's World of Warships. A user is able to click multiple times on "create" on a post creation prompt before the modal closes, which triggers sending several post creation API requests at once. Due to timing, sending multiple posts simultaneously requests bypasses the cooldown validation, however are not refreshing a user's metrics more than once, due to concurrent karma updates. This issue is fixed in 0.17.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34695.json
- https://github.com/SakuraIsayeki/WOWS-Karma/security/advisories/GHSA-v6cc-v976-mj8g
- https://nvd.nist.gov/vuln/detail/CVE-2024-34695
- https://github.com/SakuraIsayeki/WOWS-Karma/commit/3210b516fa3551e30fe760c915f7656d9046e69a
- https://github.com/SakuraIsayeki/WOWS-Karma/commit/6cb825976f28c68d79172aeda00e955bf5853de2

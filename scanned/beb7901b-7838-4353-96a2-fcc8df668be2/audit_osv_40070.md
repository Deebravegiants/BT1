# [M] Rocket.Chat: Livechat Visitor Profile Disclosure Leaks Bearer Token and Enables Visitor Impersonation

## Summary
Severity: Medium
Advisory: CVE-2026-49278
Aliases: GHSA-cqj7-h8cj-jmf2
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-49278
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 8.5.0, 8.4.2, 8.3.4, 8.2.4, 8.1.5, 8.0.6, 7.13.8, and 7.10.12, in the visitors.info endpoint, https://developer.rocket.chat/apidocs/get-visitor-information-by-id-1, token is returned in the response. It looks like there's no use case for the token to be present in the response and it would be a good security practice to remove it altogether. This vulnerability is fixed in 8.5.0, 8.4.2, 8.3.4, 8.2.4, 8.1.5, 8.0.6, 7.13.8, and 7.10.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49278.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-cqj7-h8cj-jmf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49278

# [H] v2board / Xboard Authentication Token Exposure via loginWithMailLink

## Summary
Severity: High
Advisory: CVE-2026-39912
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39912
Type: osv

## Details
V2Board 1.6.1 through 1.7.4 and Xboard through 0.1.9 expose authentication tokens in HTTP response bodies of the loginWithMailLink endpoint when the login_with_mail_link_enable feature is active. Unauthenticated attackers can POST to the loginWithMailLink endpoint with a known email address to receive the full authentication URL in the response, then exchange the token at the token2Login endpoint to obtain a valid bearer token with complete account access including admin privileges.

## References
- https://github.com/cedar2025/Xboard/blob/1fe6531924cc1ec662a88b9ef725afcf78d660bc/app/Http/Controllers/V1/Passport/AuthController.php#L51
- https://github.com/cedar2025/Xboard/blob/1fe6531924cc1ec662a88b9ef725afcf78d660bc/app/Services/Auth/MailLinkService.php#L49
- https://github.com/v2board/v2board/blob/0ca47622a50116d0ddd7ffb316b157afb57d25e8/app/Http/Controllers/Passport/AuthController.php#L71
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39912.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39912
- https://www.vulncheck.com/advisories/v2board-xboard-authentication-token-exposure-via-loginwithmaillink
- https://github.com/cedar2025/Xboard/pull/873
- https://github.com/v2board/v2board/pull/981
- https://github.com/cedar2025/Xboard/commit/121511523f04882ec0c7447acd9b8ebcb8a47957
- https://github.com/cedar2025/Xboard
- https://github.com/v2board/v2board
- https://chocapikk.com/posts/2026/xboard-v2board-account-takeover/

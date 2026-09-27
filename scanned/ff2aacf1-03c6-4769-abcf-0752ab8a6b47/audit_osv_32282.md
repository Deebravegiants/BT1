# [C] Code injection in binance-trading-bot

## Summary
Severity: Critical
Advisory: CVE-2025-27106
Aliases: GHSA-wq6j-4388-4gg5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-02-21
Source: https://osv.dev/vulnerability/CVE-2025-27106
Type: osv

## Details
binance-trading-bot is an automated Binance trading bot with trailing buy/sell strategy. Authenticated users of binance-trading-bot can achieve Remote Code Execution on the host system due to a command injection vulnerability in the `/restore` endpoint. The restore endpoint of binance-trading-bot is vulnerable to command injection via the `/restore` endpoint. The name of the uploaded file is passed to shell.exec without sanitization other than path normalization, resulting in Remote Code Execution. This may allow any authorized user to execute code in the context of the host machine. This issue has been addressed in version 0.0.100 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/chrisleekr/binance-trading-bot/blob/dd8e1a91b872a48aec47bbe1280c1c6ea96784d9/app/frontend/webserver/handlers/restore-post.js#L14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27106.json
- https://github.com/chrisleekr/binance-trading-bot/security/advisories/GHSA-wq6j-4388-4gg5
- https://nvd.nist.gov/vuln/detail/CVE-2025-27106
- https://github.com/chrisleekr/binance-trading-bot/commit/99d464cf8ef858d441189993054ec5f5f86e6213

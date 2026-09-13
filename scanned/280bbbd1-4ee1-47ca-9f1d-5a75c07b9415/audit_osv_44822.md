# [H] WWBN AVideo Unrestricted Authentication Attempts via get_api_preauthorize

## Summary
Severity: High
Advisory: CVE-2026-86729
Aliases: GHSA-vvqm-mgc5-hhx3
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86729
Type: osv

## Details
WWBN AVideo through commit e01e41ecc (no patched version available) exposes get_api_preauthorize in plugin/API/API.php as a second, undocumented login path. Unlike get_api_signIn, which enforces a rate limit of 10 attempts per 5 minutes via checkRateLimit(), get_api_preauthorize performs the same credential check with no throttling for any client, allowing unlimited remote password guessing against arbitrary accounts, including admin. The endpoint also acts as a credential oracle: it returns the message "Invalid credentials" for both correct and incorrect passwords, while the users_id field in the response body discloses the authenticated identity (users_id:1 on success, users_id:0 on failure), and a correct password establishes a session cookie that remains usable for authenticated API requests. Together these issues permit unauthenticated brute-force account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86729.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-vvqm-mgc5-hhx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-86729
- https://www.vulncheck.com/advisories/wwbn-avideo-unrestricted-authentication-attempts-via-get-api-preauthorize

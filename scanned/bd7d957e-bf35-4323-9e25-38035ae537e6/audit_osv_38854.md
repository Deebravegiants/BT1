# [H] Actual has an OpenID `client_secret` Disclosure via Broken Authorization Guard in `/openid/config`

## Summary
Severity: High
Advisory: CVE-2026-42604
Aliases: GHSA-49v6-pqjq-xw55
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-42604
Type: osv

## Details
Actual is a local-first personal finance tool. The `POST /openid/config` endpoint in Actual Budget's sync-server versions <= 26.4.0 exposes the full OpenID Connect configuration—including the OAuth2 `client_secret`—to any caller who knows the bootstrap password. The endpoint also lacks authentication and rate limiting, making the bootstrap password brute-forceable. Version 26.5.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42604.json
- https://github.com/actualbudget/actual/security/advisories/GHSA-49v6-pqjq-xw55
- https://nvd.nist.gov/vuln/detail/CVE-2026-42604
- https://actualbudget.org/blog/release-26.5.0

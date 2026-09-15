# [M] Talishar: Authentication Bypass via Empty authKey Parameter Allows Unauthenticated Game Actions

## Summary
Severity: Medium
Advisory: CVE-2026-28428
Aliases: GHSA-2659-p579-wv83
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28428
Type: osv

## Details
Talishar is a fan-made Flesh and Blood project. Prior to commit a9c218e, an authentication bypass vulnerability in Talishar's game endpoint validation logic allows any unauthenticated attacker to perform authenticated game actions — including sending chat messages and submitting game inputs — by supplying an empty authKey parameter (authKey=). The server-side validation uses a loose comparison that accepts an empty string as a valid credential, while correctly rejecting non-empty but incorrect keys. This asymmetry means the authentication mechanism can be completely bypassed without knowing any valid token. This issue has been patched in commit a9c218e.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28428.json
- https://github.com/Talishar/Talishar/commit/a9c218efa37756c9e7eed056fbff6ee03f79aefc
- https://github.com/Talishar/Talishar/security/advisories/GHSA-2659-p579-wv83
- https://nvd.nist.gov/vuln/detail/CVE-2026-28428

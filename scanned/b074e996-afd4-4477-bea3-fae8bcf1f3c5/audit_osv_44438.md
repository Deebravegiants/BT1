# [H] Rybbit Reflects Any Origin in CORS Responses While Allowing Credentials

## Summary
Severity: High
Advisory: CVE-2026-82287
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82287
Type: osv

## Details
Rybbit before 2.7.0 contains a CORS misconfiguration vulnerability that allows attackers to bypass origin restrictions by reflecting any request origin in Access-Control-Allow-Origin responses while credentials are enabled. Attackers can issue credentialed cross-origin requests from any website to read analytics data, account information, and perform authenticated state-changing operations as the victim user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82287.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82287
- https://www.vulncheck.com/advisories/rybbit-reflects-any-origin-in-cors-responses-while-allowing-credentials
- https://github.com/rybbit-io/rybbit/issues/1038
- https://github.com/rybbit-io/rybbit/commit/6f1039bdd3328a84d6700031bc0ce4714020e2f9
- https://github.com/rybbit-io/rybbit
- https://github.com/rybbit-io/rybbit/blob/v2.6.0/server/src/index.ts

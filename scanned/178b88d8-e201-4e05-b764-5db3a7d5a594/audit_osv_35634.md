# [M] Rate-limit Bypass in zenml-io/zenml

## Summary
Severity: Medium
Advisory: CVE-2026-11922
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-11922
Type: osv

## Details
A vulnerability in zenml-io/zenml versions 0.57.0 through 0.94.2 allows an attacker to bypass rate-limiting on the `POST /api/v1/login` and self password-change endpoints by rotating the `X-Forwarded-For` header. The rate limiter keys requests by `request.client.host`, which is derived from the `X-Forwarded-For` header when Uvicorn is launched with `--proxy-headers --forwarded-allow-ips *`. This configuration allows clients to control the value of `request.client.host`, effectively bypassing rate-limiting protections. This vulnerability leaves the affected endpoints open to unthrottled credential guessing attacks.

## References
- https://huntr.com/bounties/3cb8bf6a-ae55-4b38-8da3-601c666a210e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11922.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11922
- https://github.com/zenml-io/zenml/commit/8a2214bdd63eb8200ce4719d82c6f0d935e922d1

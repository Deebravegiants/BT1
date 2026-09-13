# [H] Wallos incomplete fix for CVE-2026-33407: unauthenticated httpoxy SSRF still reachable via `endpoints/payments/search.php`

## Summary
Severity: High
Advisory: CVE-2026-77348
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-77348
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 5.0.0, the fix for CVE-2026-33407 (GHSA-hhjq-82f8-m6rc, "SSRF via HTTP Proxy Environment Variable") hardened endpoints/logos/search.php by disabling cURL proxying (CURLOPT_PROXY = '' + CURLOPT_NOPROXY = '*'). However, Wallos ships a second, near-identical, unauthenticated logo-image search endpoint — endpoints/payments/search.php — that was not given the same hardening. It still passes the HTTP_PROXY/HTTPS_PROXY environment variable straight into CURLOPT_PROXY. This issue has been patched in version 5.0.0.

## References
- https://github.com/ellite/Wallos/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77348.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-f8j2-qm83-r2w4
- https://github.com/ellite/Wallos/security/advisories/GHSA-hhjq-82f8-m6rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-77348
- https://github.com/ellite/Wallos/commit/11eaf402e841a628c68a805694227ce66c45f6f3

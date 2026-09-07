# [M] next-intl has an open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8f24-v5vv-gm5j
CVE: CVE-2026-40299
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8f24-v5vv-gm5j
Type: github-advisory

## Affected
- npm: `next-intl` — affected >=0 <4.9.1

## Details
### Impact

Applications using the `next-intl` middleware with `localePrefix: 'as-needed'` could construct URLs where path handling and the WHATWG URL parser resolved a relative redirect target to another host (e.g. scheme-relative `//` or control characters stripped by the URL parser), so the middleware could redirect the browser off-site while the user still started from a trusted app URL.

### Patches

The problem has been patched, please update to [`next-intl@4.9.1`](https://github.com/amannn/next-intl/releases/tag/v4.9.1).

### Credits

Many thanks to [Joni Liljeblad](https://github.com/joniumGit) from [Oura](https://ouraring.com) for responsibly disclosing the vulnerability and for suggesting the fix.

## References
- https://github.com/amannn/next-intl/security/advisories/GHSA-8f24-v5vv-gm5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40299
- https://github.com/amannn/next-intl/pull/2304
- https://github.com/amannn/next-intl/commit/1c80b668aa6d853f470319eec10a3f61e78a70e6
- https://github.com/amannn/next-intl
- https://github.com/amannn/next-intl/releases/tag/v4.9.1

# [H] Flowise: SSRF Protection Bypass (TOCTOU & Default Insecure)

## Summary
Severity: High
Advisory: CVE-2026-41272
Aliases: GHSA-2x8m-83vc-6wv4
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41272
Type: osv

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. Prior to 3.1.0, the core security wrappers (secureAxiosRequest and secureFetch) intended to prevent Server-Side Request Forgery (SSRF) contain multiple logic flaws. These flaws allow attackers to bypass the allow/deny lists via DNS Rebinding (Time-of-Check Time-of-Use) or by exploiting the default configuration which fails to enforce any deny list. This vulnerability is fixed in 3.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41272.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-2x8m-83vc-6wv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41272

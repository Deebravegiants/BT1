# [H] LibreChat is Vulnerable to Server-Side Request Forgery (SSRF) in Actions Capability

## Summary
Severity: High
Advisory: CVE-2025-66201
Aliases: GHSA-7m2q-fjwr-5x8v
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66201
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Prior to version 0.8.1-rc2, LibreChat is vulnerable to Server-side Request Forgery (SSRF), by passing specially crafted OpenAPI specs to its "Actions" feature and making the LLM use those actions. It could be used by an authenticated user with access to this feature to access URLs only accessible to the LibreChat server (such as cloud metadata services, through which impersonation of the server might be possible). This issue has been patched in version 0.8.1-rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66201.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-7m2q-fjwr-5x8v
- https://nvd.nist.gov/vuln/detail/CVE-2025-66201

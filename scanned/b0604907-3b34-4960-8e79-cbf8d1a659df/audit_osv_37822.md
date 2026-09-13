# [H] Wallos: SSRF via HTTP Proxy Environment Variable

## Summary
Severity: High
Advisory: CVE-2026-33407
Aliases: GHSA-hhjq-82f8-m6rc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33407
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.7.0, Wallos endpoints/logos/search.php accepts HTTP_PROXY and HTTPS_PROXY environment variables without validation, enabling SSRF via proxy hijacking. The server performs DNS resolution on user-supplied search terms, which can be controlled by attackers to trigger outbound requests to arbitrary domains. This issue has been patched in version 4.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33407.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-hhjq-82f8-m6rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33407
- https://github.com/ellite/Wallos/commit/e87387f0ebb540cd33e6dfda7181db9db650ecef#diff-d77202c5d47a3d7d4586e519f6f5e256da5fb2969fa8b9c75c399b2821e9de40

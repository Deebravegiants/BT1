# [M] RustFS: Reflective CORS with credentials on S3 listener; unauthenticated license metadata endpoint on console

## Summary
Severity: Medium
Advisory: CVE-2026-46685
Aliases: GHSA-x5xv-223c-8vm7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46685
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.2, when RUSTFS_CORS_ALLOWED_ORIGINS is unset, the RustFS S3 listener's ConditionalCorsLayer reflects any request Origin value back as Access-Control-Allow-Origin and also sets Access-Control-Allow-Credentials: true and Access-Control-Allow-Headers: * on responses, including preflight responses and error responses. This creates a permissive cross-domain policy with untrusted origins. A browser visiting an attacker-controlled page can issue credentialed cross-origin requests to a reachable RustFS deployment and read the response when the victim browser has ambient credentials for the RustFS origin, such as saved HTTP Basic Auth credentials, reverse-proxy SSO cookies, or TLS client certificates. This vulnerability is fixed in 1.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46685.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-x5xv-223c-8vm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46685

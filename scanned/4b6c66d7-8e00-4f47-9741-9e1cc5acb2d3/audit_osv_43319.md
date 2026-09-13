# [H] Mongoose: TLS Hostname Verification Bypass via Overly Permissive Wildcard Matching

## Summary
Severity: High
Advisory: CVE-2026-73253
Aliases: GHSA-jp6g-796f-39vp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-73253
Type: osv

## Details
Mongoose is an embedded web server and network library. Prior to version 7.22, an on-path network attacker with a wildcard certificate for a parent domain can impersonate deeper subdomains to a client using the built-in TLS stack. The mg_tls_verify_cert_san() and mg_tls_verify_cert_cn() functions in src/tls_builtin.c call mg_match(), whose wildcard can cross DNS label boundaries, so a pattern such as *.example.com can match foo.bar.example.com. The resulting hostname verification bypass permits interception and modification of TLS traffic. This issue is fixed in version 7.22.

## References
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73253.json
- https://github.com/cesanta/mongoose/security/advisories/GHSA-jp6g-796f-39vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-73253
- https://github.com/cesanta/mongoose/commit/a9df523f76f43a38bd53b4232b9cfd4c16869e71
- https://github.com/cesanta/mongoose/pull/3611

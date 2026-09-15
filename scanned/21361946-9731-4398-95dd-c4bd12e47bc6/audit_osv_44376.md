# [M] openssl_encrypt before 1.4.9 Plugin Sandbox Path Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-81716
Aliases: GHSA-vr4h-5xqv-xxxf, PYSEC-2026-3800
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81716
Type: osv

## Details
openssl_encrypt (pip: openssl-encrypt) versions before 1.4.9 contain a path traversal flaw in PluginSandbox._is_safe_path, which authorized file access using a bare string-prefix match. A sandboxed plugin without the READ_FILES permission could read or write another plugin's directory that merely shares a name prefix (e.g., .../plugins/foobar matching allowed .../plugins/foo), breaking per-plugin isolation within the same user. Fixed by matching each allowed directory exactly or with a trailing path separator.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81716.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-vr4h-5xqv-xxxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-81716
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-plugin-sandbox-path-traversal

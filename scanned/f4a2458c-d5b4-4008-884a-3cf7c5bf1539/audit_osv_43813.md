# [M] openssl_encrypt before 1.4.0 Path Traversal via plugin_id

## Summary
Severity: Medium
Advisory: CVE-2026-74884
Aliases: GHSA-8jpj-w975-rwv5, PYSEC-2026-3761
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74884
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a path traversal vulnerability in the _is_safe_path method where the plugin_id parameter is not sanitized before constructing the plugin config directory path. Attackers can declare a malicious plugin_id containing path traversal sequences like '../' to access arbitrary directories outside the intended plugin directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74884.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-8jpj-w975-rwv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-74884
- https://www.vulncheck.com/advisories/openssl-encrypt-before-path-traversal-via-plugin-id

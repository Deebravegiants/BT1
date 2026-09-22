# [C] openssl_encrypt before 1.4.0 Sandbox Escape via Dunder Attribute Traversal

## Summary
Severity: Critical
Advisory: CVE-2026-74896
Aliases: GHSA-w7gr-9g4g-33mx, PYSEC-2026-3771
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74896
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a sandbox escape vulnerability in the DangerousPatternVisitor AST analyzer that fails to detect dunder attribute traversal techniques. Attackers can use __class__, __bases__, __subclasses__(), and __globals__ chains to access restricted functions and execute arbitrary system commands from plugin code.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74896.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-w7gr-9g4g-33mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-74896
- https://www.vulncheck.com/advisories/openssl-encrypt-before-sandbox-escape-via-dunder-attribute-traversal

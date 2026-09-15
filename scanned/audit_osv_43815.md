# [C] openssl_encrypt before 1.4.0 Plugin Import Guard Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-74886
Aliases: GHSA-9pgj-v69p-q586, PYSEC-2026-3763
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74886
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a plugin sandbox bypass vulnerability where the PluginImportGuard blocks a different set of modules than the AST analyzer's DANGEROUS_MODULES set. Attackers can bypass AST analysis through string obfuscation or encoding to import unblocked dangerous modules like sys, shutil, multiprocessing, importlib, and pickle for arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74886.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-9pgj-v69p-q586
- https://nvd.nist.gov/vuln/detail/CVE-2026-74886
- https://www.vulncheck.com/advisories/openssl-encrypt-before-plugin-import-guard-bypass

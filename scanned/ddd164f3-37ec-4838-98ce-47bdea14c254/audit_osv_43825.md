# [C] openssl_encrypt before 1.4.0 Sandbox Escape via Type Hierarchy

## Summary
Severity: Critical
Advisory: CVE-2026-74899
Aliases: PYSEC-2026-3727
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74899
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a sandbox escape vulnerability in IsolatedPluginExecutor that exposes Python type objects in restricted exec() builtins. Attackers can traverse the Python class hierarchy via __class__.__mro__.__subclasses__() to access system functions and execute arbitrary OS commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74899.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-m25m-ggxg-239c
- https://nvd.nist.gov/vuln/detail/CVE-2026-74899
- https://www.vulncheck.com/advisories/openssl-encrypt-before-sandbox-escape-via-type-hierarchy
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-43jx-gxq4-jpjc

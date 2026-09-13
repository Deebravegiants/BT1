# [C] openssl_encrypt before 1.4.9 Remote Code Execution via Plugin

## Summary
Severity: Critical
Advisory: CVE-2026-81719
Aliases: GHSA-587j-4r3v-cm2c, PYSEC-2026-3802
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81719
Type: osv

## Details
openssl_encrypt before 1.4.9 executes untrusted third-party plugins with insufficient controls: the plugin signature policy defaulted to WARN, so an unsigned/unverifiable non-built-in plugin was compiled and executed in the host process at import time, before the runtime sandbox is installed. The only default gate was an incomplete, bypassable AST denylist. If a user is induced to load an attacker's plugin, this results in arbitrary code execution with the privileges of the user running openssl_encrypt. Fixed in 1.4.9 by defaulting the signature policy to ENFORCE for non-built-in plugins.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81719.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-587j-4r3v-cm2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-81719
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-remote-code-execution-via-plugin

# [C] openssl_encrypt before 1.4.0 Plugin Sandbox Bypass via Process Isolation

## Summary
Severity: Critical
Advisory: CVE-2026-74895
Aliases: GHSA-623h-chj7-hfx8, PYSEC-2026-3770
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74895
Type: osv

## Details
openssl_encrypt versions before 1.4.0 fail to apply sandbox restrictions in the default process isolation mode for plugin execution. Attackers can execute malicious plugins with unrestricted access to the filesystem, network, subprocess execution, and all Python modules.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74895.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-623h-chj7-hfx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-74895
- https://www.vulncheck.com/advisories/openssl-encrypt-before-plugin-sandbox-bypass-via-process-isolation

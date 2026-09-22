# [C] openssl_encrypt before 1.4.0 Sandbox Bypass via pathlib and io

## Summary
Severity: Critical
Advisory: CVE-2026-74883
Aliases: GHSA-mcjj-qw7m-j3cp, PYSEC-2026-3760
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74883
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a sandbox bypass vulnerability where the plugin sandbox fails to restrict alternative file access methods like pathlib.Path and io.open. Attackers can import pathlib or io modules to read and write arbitrary files, completely bypassing the restricted_open file access controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74883.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-mcjj-qw7m-j3cp
- https://nvd.nist.gov/vuln/detail/CVE-2026-74883
- https://www.vulncheck.com/advisories/openssl-encrypt-before-sandbox-bypass-via-pathlib-and-io

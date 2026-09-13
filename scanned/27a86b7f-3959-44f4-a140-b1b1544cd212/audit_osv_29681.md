# [H] Picotls double free

## Summary
Severity: High
Advisory: CVE-2024-45402
Aliases: GHSA-w7c8-wjx9-vvvv
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-10-11
Source: https://osv.dev/vulnerability/CVE-2024-45402
Type: osv

## Details
Picotls is a TLS protocol library that allows users select different crypto backends based on their use case. When parsing a spoofed TLS handshake message, picotls (specifically, bindings within picotls that call the crypto libraries) may attempt to free the same memory twice. This double free occurs during the disposal of multiple objects without any intervening calls to malloc Typically, this triggers the malloc implementation to detect the error and abort the process. However, depending on the internals of malloc and the crypto backend being used, the flaw could potentially lead to a use-after-free scenario, which might allow for arbitrary code execution. The vulnerability is addressed with commit 9b88159ce763d680e4a13b6e8f3171ae923a535d.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45402.json
- https://github.com/h2o/picotls/security/advisories/GHSA-w7c8-wjx9-vvvv
- https://nvd.nist.gov/vuln/detail/CVE-2024-45402
- https://github.com/h2o/picotls/commit/9b88159ce763d680e4a13b6e8f3171ae923a535d

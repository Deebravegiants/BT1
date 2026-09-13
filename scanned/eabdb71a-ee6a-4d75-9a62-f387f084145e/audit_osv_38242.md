# [C] Buffer overflow in CRL number parsing in wolfSSL

## Summary
Severity: Critical
Advisory: CVE-2026-3548
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-3548
Type: osv

## Details
Two buffer overflow vulnerabilities existed in the wolfSSL CRL parser when parsing CRL numbers: a heap-based buffer overflow could occur when improperly storing the CRL number as a hexadecimal string, and a stack-based overflow for sufficiently sized CRL numbers. With appropriately crafted CRLs, either of these out of bound writes could be triggered. Note this only affects builds that specifically enable CRL support, and the user would need to load a CRL from an untrusted source.

## References
- https://github.com/wolfSSL/wolfssl/pull/9628/
- https://github.com/wolfSSL/wolfssl/pull/9873/
- https://www.wolfssl.com/download/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3548.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3548
- https://github.com/wolfSSL/wolfssl

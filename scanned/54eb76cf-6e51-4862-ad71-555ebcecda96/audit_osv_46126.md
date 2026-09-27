# [C] Two buffer overflow vulnerabilities existed in the wolfSSL CRL parser when parsing CRL numbers: a...

## Summary
Severity: Critical
Advisory: JLSEC-2026-707
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-707
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Two buffer overflow vulnerabilities existed in the wolfSSL CRL parser when parsing CRL numbers: a heap-based buffer overflow could occur when improperly storing the CRL number as a hexadecimal string, and a stack-based overflow for sufficiently sized CRL numbers. With appropriately crafted CRLs, either of these out of bound writes could be triggered. Note this only affects builds that specifically enable CRL support, and the user would need to load a CRL from an untrusted source.

## References
- https://github.com/advisories/GHSA-86fv-q5vx-mw5m
- https://github.com/wolfSSL/wolfssl/pull/9628
- https://github.com/wolfSSL/wolfssl/pull/9628/
- https://github.com/wolfSSL/wolfssl/pull/9873
- https://github.com/wolfSSL/wolfssl/pull/9873/
- https://nvd.nist.gov/vuln/detail/CVE-2026-3548

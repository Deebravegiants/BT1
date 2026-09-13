# [C] In function MatchDomainName(), input param str is treated as a NULL terminated string despite being...

## Summary
Severity: Critical
Advisory: JLSEC-2026-685
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-685
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
In function MatchDomainName(), input param str is treated as a NULL terminated string despite being user provided and unchecked. Specifically, the function `X509_check_host()` takes in a pointer and length to check against, with no requirements that it be NULL terminated. If a caller was attempting to do a name check on a non-NULL terminated buffer, the code would read beyond the bounds of the input array until it found a NULL terminator.This issue affects wolfSSL: through 5.7.0.

## References
- https://github.com/advisories/GHSA-jwjf-h4v6-qrpp
- https://github.com/wolfSSL/wolfssl/pull/7604
- https://https://github.com/wolfSSL/wolfssl/pull/7604
- https://nvd.nist.gov/vuln/detail/CVE-2024-5991

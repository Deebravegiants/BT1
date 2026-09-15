# [M] In the OpenSSL compatibility layer implementation, the function `RAND_poll()` was not behaving as...

## Summary
Severity: Medium
Advisory: JLSEC-2026-689
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-689
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.8.4+0

## Details
In the OpenSSL compatibility layer implementation, the function `RAND_poll()` was not behaving as expected and leading to the potential for predictable values returned from `RAND_bytes()` after fork() is called. This can lead to weak or predictable random numbers generated in applications that are both using `RAND_bytes()` and doing fork() operations. This only affects applications explicitly calling `RAND_bytes()` after fork() and does not affect any internal TLS operations. Although `RAND_bytes()` documentation in OpenSSL calls out not being safe for use with fork() without first calling `RAND_poll()`, an additional code change was also made in wolfSSL to make `RAND_bytes()` behave similar to OpenSSL after a fork() call without calling `RAND_poll()`. Now the Hash-DRBG used gets reseeded after detecting running in a new process. If making use of `RAND_bytes()` and calling fork() we recommend updating to the latest version of wolfSSL. Thanks to Per Allansson from Appgate for the report.

## References
- https://github.com/advisories/GHSA-jgh6-fqf6-cpj8
- https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md#wolfssl-release-582-july-17-2025
- https://nvd.nist.gov/vuln/detail/CVE-2025-7394

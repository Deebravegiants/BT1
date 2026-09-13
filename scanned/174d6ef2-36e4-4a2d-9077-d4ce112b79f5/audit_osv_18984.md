# [C] CVE-2020-5499

## Summary
Severity: Critical
Advisory: CVE-2020-5499
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-04
Source: https://osv.dev/vulnerability/CVE-2020-5499
Type: osv

## Details
Baidu Rust SGX SDK through 1.0.8 has an enclave ID race. There are non-deterministic results in which, sometimes, two global IDs are the same.

## References
- https://github.com/wssgcsc58/CVEs/tree/master/baidurustsgxsdk_enclaveid_race

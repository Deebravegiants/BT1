# [M] CVE-2021-32275

## Summary
Severity: Medium
Advisory: CVE-2021-32275
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32275
Type: osv

## Details
An issue was discovered in faust through v2.30.5. A NULL pointer dereference exists in the function CosPrim::computeSigOutput() located in cosprim.hh. It allows an attacker to cause Denial of Service.

## References
- https://github.com/grame-cncm/faust/issues/482

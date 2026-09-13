# [M] CVE-2020-23911

## Summary
Severity: Medium
Advisory: CVE-2020-23911
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2020-23911
Type: osv

## Details
An issue was discovered in asn1c through v0.9.28. A NULL pointer dereference exists in the function _default_error_logger() located in asn1fix.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/vlm/asn1c/issues/394

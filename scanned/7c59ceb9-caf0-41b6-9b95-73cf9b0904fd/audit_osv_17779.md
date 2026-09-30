# [C] CVE-2020-19692

## Summary
Severity: Critical
Advisory: CVE-2020-19692
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2020-19692
Type: osv

## Details
Buffer Overflow vulnerabilty found in Nginx NJS v.0feca92 allows a remote attacker to execute arbitrary code via the njs_module_read in the njs_module.c file.

## References
- https://github.com/nginx/njs/issues/187

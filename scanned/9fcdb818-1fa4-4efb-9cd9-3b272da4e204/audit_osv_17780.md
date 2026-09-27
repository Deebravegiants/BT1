# [C] CVE-2020-19695

## Summary
Severity: Critical
Advisory: CVE-2020-19695
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2020-19695
Type: osv

## Details
Buffer Overflow found in Nginx NJS allows a remote attacker to execute arbitrary code via the njs_object_property parameter of the njs/njs_vm.c function.

## References
- https://github.com/nginx/njs/issues/188

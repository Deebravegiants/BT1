# [M] CVE-2023-49556

## Summary
Severity: Medium
Advisory: CVE-2023-49556
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-01-03
Source: https://osv.dev/vulnerability/CVE-2023-49556
Type: osv

## Details
Buffer Overflow vulnerability in YASM 1.3.0.86.g9def allows a remote attacker to cause a denial of service via the expr_delete_term function in the libyasm/expr.c component.

## References
- https://github.com/yasm/yasm/issues/250

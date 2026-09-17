# [M] CVE-2020-29561

## Summary
Severity: Medium
Advisory: CVE-2020-29561
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-04
Source: https://osv.dev/vulnerability/CVE-2020-29561
Type: osv

## Details
An issue was discovered in SonicBOOM riscv-boom 3.0.0. For LR, it does not avoid acquiring a reservation in the case where a load translates successfully but still generates an exception.

## References
- https://github.com/riscv-boom/riscv-boom/issues/504#issuecomment-736196635

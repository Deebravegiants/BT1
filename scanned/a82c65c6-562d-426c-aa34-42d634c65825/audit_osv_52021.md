# [M] CVE-2021-46974

## Summary
Severity: Medium
Advisory: CVE-2021-46974
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46974
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix masking negation logic upon negative dst register

The negation logic for the case where the off_reg is sitting in the
dst register is not correct given then we cannot just invert the add
to a sub or vice versa. As a fix, perform the final bitwise and-op
unconditionally into AX from the off_reg, then move the pointer from
the src to dst and finally use AX as the source for the original
pointer arithmetic operation such that the inversion yields a correct
result. The single non-AX mov in between is possible given constant
blinding is retaining it as it's not an immediate based operation.

## References
- https://git.kernel.org/stable/c/4d542ddb88fb2f39bf7f14caa2902f3e8d06f6ba
- https://git.kernel.org/stable/c/53e0db429b37a32b8fc706d0d90eb4583ad13848
- https://git.kernel.org/stable/c/6eba92a4d4be8feb4dc33976abac544fa99d6ecc
- https://git.kernel.org/stable/c/7cf64d8679ca1cb20cf57d6a88bfee79a0922a66
- https://git.kernel.org/stable/c/b9b34ddbe2076ade359cd5ce7537d5ed019e9807
- https://git.kernel.org/stable/c/0e2dfdc74a7f4036127356d42ea59388f153f42c
- https://git.kernel.org/stable/c/2cfa537674cd1051a3b8111536d77d0558f33d5d

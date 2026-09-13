# [M] BIT-pytorch-2025-46152

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-46152
Aliases: CVE-2025-46152, PYSEC-2025-201
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-46152
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
In PyTorch before 2.7.0, bitwise_right_shift produces incorrect output for certain out-of-bounds values of the "other" argument.

## References
- https://gist.github.com/shaoyuyoung/4bcefba4004f8271e64b5185c95a248a
- https://github.com/pytorch/pytorch/issues/143555
- https://github.com/pytorch/pytorch/pull/143635
- https://nvd.nist.gov/vuln/detail/CVE-2025-46152

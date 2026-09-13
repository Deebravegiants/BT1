# [M] BIT-pytorch-2024-31584

## Summary
Severity: Medium
Advisory: BIT-pytorch-2024-31584
Aliases: CVE-2024-31584, PYSEC-2024-250
Ecosystem: Bitnami
Published: 2025-06-04
Source: https://osv.dev/vulnerability/BIT-pytorch-2024-31584
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.2.1

## Details
Pytorch before v2.2.0 has an Out-of-bounds Read vulnerability via the component torch/csrc/jit/mobile/flatbuffer_loader.cpp.

## References
- https://github.com/pytorch/pytorch/blob/v2.1.2/torch/csrc/jit/mobile/flatbuffer_loader.cpp#L305
- https://github.com/pytorch/pytorch/commit/7c35874ad664e74c8e4252d67521f3986eadb0e6
- https://nvd.nist.gov/vuln/detail/CVE-2024-31584

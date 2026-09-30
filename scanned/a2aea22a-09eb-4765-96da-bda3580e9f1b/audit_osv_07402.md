# [H] BIT-pytorch-2025-55560

## Summary
Severity: High
Advisory: BIT-pytorch-2025-55560
Aliases: CVE-2025-55560, PYSEC-2025-209
Ecosystem: Bitnami
Published: 2025-10-15
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-55560
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.7.1

## Details
An issue in pytorch v2.7.0 can lead to a Denial of Service (DoS) when a PyTorch model consists of torch.Tensor.to_sparse() and torch.Tensor.to_dense() and is compiled by Inductor.

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/pytorch/pytorch/issues/151522
- https://github.com/pytorch/pytorch/pull/151897
- https://nvd.nist.gov/vuln/detail/CVE-2025-55560

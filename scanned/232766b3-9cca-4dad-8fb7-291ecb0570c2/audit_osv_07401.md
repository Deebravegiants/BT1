# [H] BIT-pytorch-2025-55558

## Summary
Severity: High
Advisory: BIT-pytorch-2025-55558
Aliases: CVE-2025-55558, PYSEC-2025-208
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-55558
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.7.1

## Details
A buffer overflow occurs in pytorch v2.7.0 when a PyTorch model consists of torch.nn.Conv2d, torch.nn.functional.hardshrink, and torch.Tensor.view-torch.mv() and is compiled by Inductor, leading to a Denial of Service (DoS).

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/pytorch/pytorch/issues/151523
- https://github.com/pytorch/pytorch/pull/151887
- https://nvd.nist.gov/vuln/detail/CVE-2025-55558

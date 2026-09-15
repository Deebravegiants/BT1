# [H] BIT-pytorch-2025-55552

## Summary
Severity: High
Advisory: BIT-pytorch-2025-55552
Aliases: CVE-2025-55552, PYSEC-2025-204
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-55552
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.9.0

## Details
pytorch v2.8.0 was discovered to display unexpected behavior when the components torch.rot90 and torch.randn_like are used together.

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/pytorch/pytorch/issues/147847
- https://nvd.nist.gov/vuln/detail/CVE-2025-55552

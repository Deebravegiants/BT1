# [H] BIT-pytorch-2025-55551

## Summary
Severity: High
Advisory: BIT-pytorch-2025-55551
Aliases: CVE-2025-55551, PYSEC-2025-203
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-55551
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.9.0

## Details
An issue in the component torch.linalg.lu of pytorch v2.8.0 allows attackers to cause a Denial of Service (DoS) when performing a slice operation.

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/pytorch/pytorch/issues/151401
- https://nvd.nist.gov/vuln/detail/CVE-2025-55551

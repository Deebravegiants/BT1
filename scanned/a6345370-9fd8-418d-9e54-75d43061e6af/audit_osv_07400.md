# [H] BIT-pytorch-2025-55557

## Summary
Severity: High
Advisory: BIT-pytorch-2025-55557
Aliases: CVE-2025-55557, PYSEC-2025-207
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-55557
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.7.1

## Details
A Name Error occurs in pytorch v2.7.0 when a PyTorch model consists of torch.cummin and is compiled by Inductor, leading to a Denial of Service (DoS).

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/pytorch/pytorch/issues/151738
- https://github.com/pytorch/pytorch/pull/151931
- https://nvd.nist.gov/vuln/detail/CVE-2025-55557

# [H] PyTorch pt2 Loading deserialization

## Summary
Severity: High
Advisory: BIT-pytorch-2026-4538
Aliases: CVE-2026-4538, PYSEC-2026-139
Ecosystem: Bitnami
Published: 2026-04-30
Source: https://osv.dev/vulnerability/BIT-pytorch-2026-4538
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.10.0 <2.11.0

## Details
A vulnerability was identified in PyTorch 2.10.0. The affected element is an unknown function of the component pt2 Loading Handler. The manipulation leads to deserialization. The attack can only be performed from a local environment. The exploit is publicly available and might be used. The project was informed of the problem early through a pull request but has not reacted yet.

## References
- https://github.com/pytorch/pytorch/
- https://github.com/pytorch/pytorch/pull/176791
- https://nvd.nist.gov/vuln/detail/CVE-2026-4538
- https://vuldb.com/?ctiid.352326
- https://vuldb.com/?id.352326
- https://vuldb.com/?submit.774681

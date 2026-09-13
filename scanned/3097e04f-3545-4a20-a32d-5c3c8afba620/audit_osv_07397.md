# [M] BIT-pytorch-2025-46153

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-46153
Aliases: CVE-2025-46153, PYSEC-2025-202
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-46153
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
PyTorch before 3.7.0 has a bernoulli_p decompose function in decompositions.py even though it lacks full consistency with the eager CPU implementation, negatively affecting nn.Dropout1d, nn.Dropout2d, and nn.Dropout3d for fallback_random=True.

## References
- https://gist.github.com/shaoyuyoung/4bcefba4004f8271e64b5185c95a248a
- https://gist.github.com/shaoyuyoung/e636f2e7a306105b7e96809e2b85c28a
- https://github.com/pytorch/pytorch/compare/v2.6.0...v2.7.0
- https://github.com/pytorch/pytorch/issues/142853
- https://github.com/pytorch/pytorch/pull/143460
- https://nvd.nist.gov/vuln/detail/CVE-2025-46153

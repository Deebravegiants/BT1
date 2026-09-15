# [M] PyTorch torch.jit.script memory corruption

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-3000
Aliases: CVE-2025-3000, GHSA-rrmf-rvhw-rf47, PYSEC-2025-194
Ecosystem: Bitnami
Published: 2025-05-30
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-3000
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
A vulnerability classified as critical has been found in PyTorch 2.6.0. This affects the function torch.jit.script. The manipulation leads to memory corruption. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/pytorch/pytorch/issues/149623
- https://github.com/pytorch/pytorch/issues/149623#issue-2935703015
- https://nvd.nist.gov/vuln/detail/CVE-2025-3000
- https://vuldb.com/?ctiid.302049
- https://vuldb.com/?id.302049
- https://vuldb.com/?submit.524197

# [M] PyTorch torch.jit.jit_module_from_flatbuffer memory corruption

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-3121
Aliases: CVE-2025-3121, PYSEC-2025-196
Ecosystem: Bitnami
Published: 2025-05-28
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-3121
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
A vulnerability classified as problematic has been found in PyTorch 2.6.0. Affected is the function torch.jit.jit_module_from_flatbuffer. The manipulation leads to memory corruption. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/pytorch/pytorch/issues/149800
- https://github.com/pytorch/pytorch/issues/149800#issue-2940240700
- https://nvd.nist.gov/vuln/detail/CVE-2025-3121
- https://vuldb.com/?ctiid.303012
- https://vuldb.com/?id.303012
- https://vuldb.com/?submit.525049

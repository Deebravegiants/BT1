# [H] PyTorch Tuple torch.ops.profiler._call_end_callbacks_on_jit_fut memory corruption

## Summary
Severity: High
Advisory: BIT-pytorch-2025-2148
Aliases: CVE-2025-2148, GHSA-c678-jfcj-6jmf, PYSEC-2025-189
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-2148
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
A vulnerability was found in PyTorch 2.6.0+cu124. It has been declared as critical. Affected by this vulnerability is the function torch.ops.profiler._call_end_callbacks_on_jit_fut of the component Tuple Handler. The manipulation of the argument None leads to memory corruption. The attack can be launched remotely. The complexity of an attack is rather high. The exploitation appears to be difficult.

## References
- https://github.com/pytorch/pytorch/issues/147722
- https://nvd.nist.gov/vuln/detail/CVE-2025-2148
- https://vuldb.com/?ctiid.299059
- https://vuldb.com/?id.299059
- https://vuldb.com/?submit.505959

# [M] PyTorch CUDACachingAllocator.cpp torch.cuda.memory.caching_allocator_delete memory corruption

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-3136
Aliases: CVE-2025-3136, PYSEC-2025-197
Ecosystem: Bitnami
Published: 2025-05-29
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-3136
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
A vulnerability, which was classified as problematic, has been found in PyTorch 2.6.0. This issue affects the function torch.cuda.memory.caching_allocator_delete of the file c10/cuda/CUDACachingAllocator.cpp. The manipulation leads to memory corruption. An attack has to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/ARPANET-cybersecurity/vuldb/issues/2
- https://github.com/pytorch/pytorch/issues/149821
- https://github.com/pytorch/pytorch/issues/149821#issue-2940838975
- https://github.com/pytorch/pytorch/issues/149821#issuecomment-2765311086
- https://nvd.nist.gov/vuln/detail/CVE-2025-3136
- https://vuldb.com/?ctiid.303041
- https://vuldb.com/?id.303041
- https://vuldb.com/?submit.525252

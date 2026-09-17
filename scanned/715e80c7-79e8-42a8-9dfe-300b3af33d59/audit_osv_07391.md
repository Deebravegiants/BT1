# [M] PyTorch torch.mkldnn_max_pool2d denial of service

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-2953
Aliases: CVE-2025-2953, GHSA-3749-ghw9-m3mg, PYSEC-2025-191
Ecosystem: Bitnami
Published: 2025-04-16
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-2953
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
A vulnerability, which was classified as problematic, has been found in PyTorch 2.6.0+cu124. Affected by this issue is the function torch.mkldnn_max_pool2d. The manipulation leads to denial of service. An attack has to be approached locally. The exploit has been disclosed to the public and may be used. The real existence of this vulnerability is still doubted at the moment. The security policy of the project warns to use unknown models which might establish malicious effects.

## References
- https://github.com/pytorch/pytorch/issues/149274
- https://github.com/pytorch/pytorch/issues/149274#issue-2923122269
- https://nvd.nist.gov/vuln/detail/CVE-2025-2953
- https://vuldb.com/?ctiid.302006
- https://vuldb.com/?id.302006
- https://vuldb.com/?submit.521279
- https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models

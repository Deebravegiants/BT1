# [M] PyTorch torch.lstm_cell memory corruption

## Summary
Severity: Medium
Advisory: BIT-pytorch-2025-3001
Aliases: CVE-2025-3001, GHSA-qfhq-4f3w-5fph, PYSEC-2025-195
Ecosystem: Bitnami
Published: 2025-05-30
Source: https://osv.dev/vulnerability/BIT-pytorch-2025-3001
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=2.6.0 <2.7.0

## Details
A vulnerability classified as critical was found in PyTorch 2.6.0. This vulnerability affects the function torch.lstm_cell. The manipulation leads to memory corruption. The attack needs to be approached locally. The exploit has been disclosed to the public and may be used.

## References
- https://github.com/pytorch/pytorch/issues/149626
- https://github.com/pytorch/pytorch/issues/149626#issue-2935860995
- https://nvd.nist.gov/vuln/detail/CVE-2025-3001
- https://vuldb.com/?ctiid.302050
- https://vuldb.com/?id.302050
- https://vuldb.com/?submit.524212

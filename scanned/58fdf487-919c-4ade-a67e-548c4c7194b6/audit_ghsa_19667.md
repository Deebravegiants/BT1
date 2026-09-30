# [M] PyTorch is vulnerable to memory corruption through its unpack_sequence function

## Summary
Severity: Medium
Advisory: GHSA-vgrw-7cvw-pwgx
CVE: CVE-2025-2999
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-vgrw-7cvw-pwgx
Type: github-advisory

## Affected
- PyPI: `torch` — affected >=0 <2.9.1

## Details
A vulnerability was found in PyTorch 2.6.0. It has been rated as critical. Affected by this issue is the function torch.nn.utils.rnn.unpack_sequence. The manipulation leads to memory corruption. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used.

A patch is available through commit [4945180](https://github.com/pytorch/pytorch/commit/494518046816d29099b7d056a74ffa5c244fdcdd).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2999
- https://github.com/pytorch/pytorch/issues/149622
- https://github.com/pytorch/pytorch/issues/149622#issue-2935495265
- https://github.com/pytorch/pytorch/commit/494518046816d29099b7d056a74ffa5c244fdcdd
- https://github.com/pypa/advisory-database/tree/main/vulns/torch/PYSEC-2025-193.yaml
- https://github.com/pytorch/pytorch
- https://vuldb.com/?ctiid.302048
- https://vuldb.com/?id.302048
- https://vuldb.com/?submit.524198

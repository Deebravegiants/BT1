# [H] TorchServe gRPC Port Exposure

## Summary
Severity: High
Advisory: GHSA-hhpg-v63p-wp7w
CVE: CVE-2024-35199
CWE: CWE-1256, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2024-07-18
Source: https://github.com/advisories/GHSA-hhpg-v63p-wp7w
Type: github-advisory

## Affected
- PyPI: `torchserve` — affected >=0.3.0 <0.11.0

## Details
### Impact
The two gRPC ports 7070 and 7071, are not bound to [localhost](http://localhost/) by default, so when TorchServe is launched, these two interfaces are bound to all interfaces. Customers using PyTorch inference Deep Learning Containers (DLC) through Amazon SageMaker and EKS are not affected.

### Patches
This issue in TorchServe has been fixed in [#3083](https://github.com/pytorch/serve/pull/3083).

TorchServe release 0.11.0 includes the fix to address this vulnerability.

### References
* [#3083](https://github.com/pytorch/serve/pull/3083)
* [TorchServe release v0.11.0](https://github.com/pytorch/serve/releases/tag/v0.11.0)

Thank Kroll Cyber Risk for for responsibly disclosing this issue.

If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/pytorch/serve/security/advisories/GHSA-hhpg-v63p-wp7w
- https://nvd.nist.gov/vuln/detail/CVE-2024-35199
- https://github.com/pytorch/serve/pull/3083
- https://github.com/pytorch/serve/commit/aab99506a17193de217aacc1119d9381dbc6ed2b
- https://github.com/pytorch/serve
- https://github.com/pytorch/serve/releases/tag/v0.11.0

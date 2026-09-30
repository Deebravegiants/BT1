# [C] TorchServe vulnerable to bypass of allowed_urls configuration

## Summary
Severity: Critical
Advisory: GHSA-wxcx-gg9c-fwp2
CVE: CVE-2024-35198
CWE: CWE-22, CWE-706
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-18
Source: https://github.com/advisories/GHSA-wxcx-gg9c-fwp2
Type: github-advisory

## Affected
- PyPI: `torchserve` — affected >=0 <0.11.0

## Details
### Impact
TorchServe's check on allowed_urls configuration can be by-passed if the URL contains characters such as ".." but it does not prevent the model from being downloaded into the model store. Once a file is downloaded, it can be referenced without providing a URL the second time, which effectively bypasses the allowed_urls security check. Customers using PyTorch inference Deep Learning Containers (DLC) through Amazon SageMaker and EKS are not affected.

### Patches
This issue in TorchServe has been fixed by validating the URL without characters such as ".." before downloading: [#3082](https://github.com/pytorch/serve/pull/3082).

TorchServe release 0.11.0 includes the fix to address this vulnerability.

### References
* [#3082](https://github.com/pytorch/serve/pull/3082)
* [TorchServe release v0.11.0](https://github.com/pytorch/serve/releases/tag/v0.11.0)

Thank Kroll Cyber Risk for for responsibly disclosing this issue.

If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/pytorch/serve/security/advisories/GHSA-wxcx-gg9c-fwp2
- https://nvd.nist.gov/vuln/detail/CVE-2024-35198
- https://github.com/pytorch/serve/pull/3082
- https://github.com/pytorch/serve/commit/cdba0fd449c2fd23dcf37c54c0784035541d5114
- https://github.com/pytorch/serve
- https://github.com/pytorch/serve/releases/tag/v0.11.0

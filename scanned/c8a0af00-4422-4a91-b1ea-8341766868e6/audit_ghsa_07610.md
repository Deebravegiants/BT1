# [H] SageMaker Python SDK has Insecure TLS Configuration

## Summary
Severity: High
Advisory: GHSA-62rc-f4v9-h543
CVE: CVE-2026-1778
CWE: CWE-295, CWE-599
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-62rc-f4v9-h543
Type: github-advisory

## Affected
- PyPI: `sagemaker` — affected >=3.0 <3.1.1
- PyPI: `sagemaker` — affected >=0 <2.256.0

## Details
### Summary
SageMaker Python SDK is an open source library for training and deploying machine learning models on Amazon SageMaker. An issue where SSL certificate verification was globally disabled in the Triton Python backend has been found.

### Impact
Arbitrary Code Execution: Disabling SSL verification allows third parties to intercept HTTPS traffic and replace models or dependencies with inappropriate versions. This could lead to remote code execution in the Triton container.

### Impacted versions

- SageMaker Python SDK v3 < v3.1.1
- SageMaker Python SDK v2 < v2.256.0

### Patches
This issue has been addressed in SageMaker Python SDK version [v3.1.1](https://github.com/aws/sagemaker-python-sdk/tree/1ab6d30401946e92fdbea18497675681649e0153) and [v2.256.0](https://github.com/aws/sagemaker-python-sdk/tree/a140cfcd12abfee10254cb4dea3bb10758e4321c). It is recommended to upgrade to the latest version immediately and ensure any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Customers using self-signed certificates for internal model downloads should add their private Certificate Authority (CA) certificate to the container image rather than relying on the SDK’s previous insecure configuration. This opt-in approach maintains security while accommodating internal trusted domains.

### References
If there are any questions or comments about this advisory, contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-62rc-f4v9-h543
- https://nvd.nist.gov/vuln/detail/CVE-2026-1778
- https://github.com/aws/sagemaker-python-sdk/commit/5e7a3efa7bec0a161194ffa0cef346dda93bf2c6
- https://github.com/aws/sagemaker-python-sdk/commit/c8098958910f7db78d07037425debfd4d44a6964
- https://aws.amazon.com/security/security-bulletins/2026-004-AWS
- https://github.com/aws/sagemaker-python-sdk
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v2.256.0
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v3.1.1

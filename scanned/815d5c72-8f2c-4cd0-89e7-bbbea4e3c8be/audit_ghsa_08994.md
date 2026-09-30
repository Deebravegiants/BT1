# [M] Amazon SageMaker Python SDK is missing integrity verification in its Triton inference handler

## Summary
Severity: Medium
Advisory: GHSA-rq6v-x3j8-7qgf
CVE: CVE-2026-8597
CWE: CWE-354
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-rq6v-x3j8-7qgf
Type: github-advisory

## Affected
- PyPI: `sagemaker` — affected >=2.199.0 <2.257.2
- PyPI: `sagemaker` — affected >=3.0.0 <3.8.0

## Details
## Summary
Amazon SageMaker Python SDK is an open-source library for training and deploying machine learning models on Amazon SageMaker. An issue exists where, under certain circumstances, the Triton inference handler deserializes model artifacts without performing integrity verification, allowing specially crafted pickle payloads to execute arbitrary code.

## Impact
When using ModelBuilder with the Triton inference server, the Triton handler did not perform integrity verification before deserializing model artifacts. A remote authenticated actor with S3 write access to the model artifact path could replace model files with a crafted payload that would execute automatically on the next container lifecycle event, achieving code execution with the SageMaker execution role's IAM permissions.


**Impacted versions:** >= v2.199.0 AND <= v2.257.1, >= v3.0.0 AND <= v3.7.1

## Patches
This issue has been addressed in Amazon SageMaker Python SDK v2.257.2 and v3.8.0. The Triton inference handler now performs integrity verification before deserializing model artifacts. AWS recommend upgrading to the latest version and rebuilding any Triton models previously created with ModelBuilder using the updated SDK. Ensure any forked or derivative code is patched to incorporate the new fixes.

## Workarounds
If upgrading is not immediately possible, users should restrict S3 write access to model artifact paths to only trusted principals and monitor for unintended modifications to files in model artifact S3 locations.

## References
If there any questions or comments about this advisory, contact AWS Security via [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-rq6v-x3j8-7qgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-8597
- https://aws.amazon.com/security/security-bulletins/2026-031-aws
- https://github.com/aws/sagemaker-python-sdk
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v2.257.2
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v3.8.0

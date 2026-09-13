# [H] SageMaker Python SDK has Exposed HMAC

## Summary
Severity: High
Advisory: GHSA-rjrp-m2jw-pv9c
CVE: CVE-2026-1777
CWE: CWE-201, CWE-295, CWE-319
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-rjrp-m2jw-pv9c
Type: github-advisory

## Affected
- PyPI: `sagemaker` — affected >=3.0 <3.2.0
- PyPI: `sagemaker` — affected >=0 <2.256.0

## Details
### Summary

SageMaker Python SDK is an open source library for training and deploying machine learning models on Amazon SageMaker. An issue where the HMAC secret key is stored in environment variables and disclosed via the DescribeTrainingJob API has been identified.

### Impact

- Function and Payload Tampering: Attackers with DescribeTrainingJob permissions may extract HMAC secret keys and forge serialized function payloads stored in S3. These tampered payloads would be processed and executed without triggering integrity validation errors, enabling unintended code substitution.
- Arbitrary Code Execution in the Training Environment: An third party with both DescribeTrainingJob permissions and write access to the job's S3 output location can extract the HMAC key, craft inappropriate Python objects, and achieve remote code execution in the client's Python process when the victim retrieves remote function results.
- Data and Credentials Handling: Arbitrary remote code execution may interact with sensitive data, model artifacts, environment variables, and potentially AWS metadata.
- Cross-Tenant or Shared Environment Risks: In multi-tenant, shared S3 bucket, a disclosed HMAC key could act as a pivot point to perform inappropriate actions against other users' remote function workloads. This could leverage the IAM permissions, shared S3 buckets, or VPC resources to compromise adjacent services or data.

### Impacted versions

- SageMaker Python SDK v3 < v3.2.0
- SageMaker Python SDK v2 < v2.256.0

### Patches
This issue has been addressed in SageMaker Python SDK version [v3.2.0](https://github.com/aws/sagemaker-python-sdk/tree/22d30f577a6139431a1fb9154b7b88a0e2a1ace6) and [v2.256.0](https://github.com/aws/sagemaker-python-sdk/tree/a140cfcd12abfee10254cb4dea3bb10758e4321c). Upgrading to the latest version immediately and ensuring any forked or derivative code is patched to incorporate the new fixes is recommended.

### Workarounds
Customers using self-signed certificates for internal model downloads should add their private Certificate Authority (CA) certificate to the container image rather than relying on the SDK’s previous insecure configuration. This opt-in approach maintains security while accommodating internal trusted domains.

### Resources
If there are any questions or comments about this advisory, contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-rjrp-m2jw-pv9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-1777
- https://github.com/aws/sagemaker-python-sdk/commit/708c7b2f4135ecaec55973d098f3dbe98b657933
- https://github.com/aws/sagemaker-python-sdk/commit/fb0d789db4fd5fecde5509963939369f4c7ce63b
- https://aws.amazon.com/security/security-bulletins/2026-004-AWS
- https://github.com/aws/sagemaker-python-sdk
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v2.256.0
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v3.2.0

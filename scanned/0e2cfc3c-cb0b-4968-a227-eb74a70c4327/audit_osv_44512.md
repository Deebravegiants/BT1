# [M] Cleartext storage of HMAC signing key in Amazon SageMaker Python SDK @step/@remote pipeline path

## Summary
Severity: Medium
Advisory: CVE-2026-83551
Aliases: GHSA-7xmc-crrw-fv5r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83551
Type: osv

## Details
Cleartext storage of sensitive information in the @step and @remote decorator pipeline component in Amazon SageMaker Python SDK before v3.11.0 and v2.256.0 might allow an authenticated remote user to extract the HMAC signing key from SageMaker DescribePipeline API responses and forge valid integrity signatures for specially crafted function payloads, achieving code execution in another user's pipeline execution context within the same AWS account.

## References
- https://aws.amazon.com/security/security-bulletins/2026-093-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83551.json
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-7xmc-crrw-fv5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-83551
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v2.256.0
- https://github.com/aws/sagemaker-python-sdk/releases/tag/v3.11.0

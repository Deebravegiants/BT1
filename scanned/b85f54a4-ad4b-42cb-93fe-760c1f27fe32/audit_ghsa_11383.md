# [H] SageMaker Python SDK replaced eval() with safe parser in JumpStart search functionality

## Summary
Severity: High
Advisory: GHSA-5r2p-pjr8-7fh7
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-5r2p-pjr8-7fh7
Type: github-advisory

## Affected
- PyPI: `sagemaker` — affected >=0 <3.4.0

## Details
## Summary

This advisory addresses the use of the search_hub() function within the SageMaker Python SDK's JumpStart search functionality. An actor with the ability to control query parameters passed to the search_hub() function could potentially provide malformed input that causes the eval() function to execute arbitrary commands, access sensitive data, or compromise the execution environment.

A defense-in-depth enhancement has been implemented to replace code evaluation with safe string operations when processing search query parameters. This enhancement removes the use of eval() from the execution path, replacing it with a safe recursive descent parser. The change was released in SageMaker Python SDK version 3.4.0 on January 23, 2026. This advisory is informational to help customers understand their responsibilities regarding input validation and configuration security under the [AWS Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/).


## Impact

Customer applications that pass unsanitized or untrusted input directly to the search_hub() function's query parameter could be prone to Remote Code Execution (RCE), potentially allowing attackers to execute arbitrary commands, access sensitive data, or compromise the execution environment. While the SDK was functioning within the requirements of the shared responsibility model—where input sanitization falls on the customer side—additional safeguards have been added to support secure customer implementations and provide defense-in-depth protection.

**Impacted versions:** All versions of SageMaker Python SDK prior to 3.4.0


## Patches

On January 23, 2026, an enhancement was made to SageMaker Python SDK version 3.4.0, which replaces eval() with a safe recursive descent parser that uses string operations for pattern matching with proper operator precedence and exception handling. We recommend upgrading to version 3.4.0 or later, using the following command:

```
pip install --upgrade sagemaker>=3.4.0
```
Customers using forked or derivative code should incorporate the fixes from the referenced pull request.

## Workarounds

No workarounds are needed, but as always you should ensure that your application is following security best practices:
- Sanitize and validate input to SDK methods to ensure only expected formats are processed
- Update to the latest SageMaker Python SDK release on a regular basis
- Follow AWS security best practices for SDK configuration and usage
- Ensure proper access controls are in place for environments where the SDK is deployed


## References

- Fixed in PR: https://github.com/aws/sagemaker-python-sdk/pull/5497
- Release: https://pypi.org/project/sagemaker/3.4.0/
- AWS Shared Responsibility Model: https://aws.amazon.com/compliance/shared-responsibility-model/

If you have any questions or comments about this advisory, contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting/) or email [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.


## Acknowledgement

We thank Dan Aridor (@daridor9) and the security research community for bringing these customer security considerations to our attention through the coordinated disclosure process and for collaborating on this issue through responsible disclosure practices.

## References
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-5r2p-pjr8-7fh7
- https://github.com/aws/sagemaker-python-sdk/pull/5497
- https://github.com/aws/sagemaker-python-sdk/commit/e706e578519bd9b92ea44b9b15f872eca5e77ea4
- https://github.com/aws/sagemaker-python-sdk

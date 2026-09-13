# [M] AWS SageMaker Training Toolkit logs CodeArtifact Authorization token

## Summary
Severity: Medium
Advisory: GHSA-635v-pc42-fr74
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-635v-pc42-fr74
Type: github-advisory

## Affected
- PyPI: `sagemaker-training` — affected >=4.7.0 <4.8.0

## Details
## Description
For SageMaker Training Toolkit[1] versions 4.7.4; 4.7.3; 4.7.2; 4.7.1; 4.7.0, the authorization tokens for CodeArtifact (temporary token with an expiration of 12 hours) were logged in the log files when the CodeArtifact capability was enabled. If customers push these log files to their CloudWatch Log streams, anyone having access to cloudwatch logs within their AWS account, may be abe to see the authorization token. If the token is not expired, they may use the authorization token to publish or consume CodeArtifact package versions.

This issue was addressed in version 4.8.0. We recommend users upgrade to version 4.8.0 or higher.  

Please note that users can add SageMaker Training Toolkit to any Docker container[2] used for SageMaker training[3]. It also comes pre-packaged with the prebuilt SageMaker Docker image[4] for SageMaker training. 

## Patches
This issue has been addressed in version 4.8.0 and higher.

## Workarounds
N/A

## References
N/A

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page[5] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] https://github.com/aws/sagemaker-training-toolkit
[2] https://www.docker.com/resources/what-container/
[3] https://aws.amazon.com/sagemaker/train/
[4] https://docs.aws.amazon.com/sagemaker/latest/dg/pre-built-containers-frameworks-deep-learning.html
[5] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/aws/sagemaker-training-toolkit/security/advisories/GHSA-635v-pc42-fr74
- https://github.com/aws/sagemaker-training-toolkit/commit/d8e56c90fa7fcc7421c0f7193bf9650fc2967213
- https://github.com/aws/sagemaker-training-toolkit

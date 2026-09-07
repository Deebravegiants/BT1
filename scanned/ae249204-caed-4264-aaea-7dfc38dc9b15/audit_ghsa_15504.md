# [M] Sensitive Information Exposure Through Insecure Logging For Secrets Like Metadata.DockerBuildArgs

## Summary
Severity: Medium
Advisory: GHSA-rjc6-vm4h-85cg
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-rjc6-vm4h-85cg
Type: github-advisory

## Affected
- PyPI: `aws-sam-cli` — affected >=0 <1.122.0

## Details
### Summary
The AWS Serverless Application Model (SAM) CLI is an open source tool that allows customers to build, deploy and test their serverless applications built on AWS. AWS SAM CLI can build container (Docker) images and customers can specify arguments in the SAM template that are passed to the Docker engine during build [1].

### Impact
If customers specify sensitive data in the DockerBuildArgs parameter of their template, the sensitive data will be shown in clear text in the AWS SAM CLI output via STDERR  when running the sam build command.

### Patches
A patch is included in aws-sam-cli>=1.122.0.

We strongly recommend customers install AWS SAM CLI v1.122.0 or above. Please review logs produced by your SAM CLI runs if you have used the DockerBuildArgs parameter and consider rotating the secrets if you believe they were exposed.

### References
If you have any questions or comments about this issue, we ask that you contact AWS/Amazon Security via our vulnerability reporting page [2] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-build.html#build-container-image 

[2] https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/aws/aws-sam-cli/security/advisories/GHSA-rjc6-vm4h-85cg
- https://github.com/aws/aws-sam-cli

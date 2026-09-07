# [H] Amazon ECS Container Agent (Windows) is vulnerable to Information Disclosure

## Summary
Severity: High
Advisory: GHSA-fc67-c4hg-q653
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-fc67-c4hg-q653
Type: github-advisory

## Affected
- Go: `github.com/aws/amazon-ecs-agent` — affected >=1.47.0 <1.103.0

## Details
### Summary
[Amazon Elastic Container Service (Amazon ECS)](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html) is a fully managed container orchestration service that enables customers to deploy, manage, and scale containerized applications. An issue exists where, under certain circumstances, improper input validation in the FSx Windows File Server volume mounting process allows command injection through specially crafted credentials. 

### Impact
Improper neutralization of inputs used in an OS command in the FSx Windows File Server volume mounting component in Amazon ECS Agent on Windows before 1.103.0 might allow a remote authenticated threat actor to execute shell commands with SYSTEM privileges on the underlying host via a specially crafted username field in an ECS task definition. This issue requires permissions to register ECS task definitions or write to the Secrets Manager or SSM Parameter Store credentials used by the FSx volume configuration.


To remediate this issue, users should upgrade to version 1.103.0.

**Impacted versions**: Version 1.47.0 through 1.102.2 of the ECS Agent for Windows

### Patches
This issue only impacts ECS Windows worker instances. ECS on Fargate is not affected. This issue has been addressed in ECS agent version 1.103.0.  Amazon ECS recommends [upgrading](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_window-container_instance.html) to the [latest](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-windows-ami-versions.html) Amazon ECS-optimized Windows AMI with an updated ECS agent version.

### Workarounds
Customers who cannot update to the latest AMI can restrict ecs:RegisterTaskDefinition permissions to trusted IAM principals only and restrict write access to Secrets Manager secrets referenced in FSx volume configurations.

### References
If you have any questions or comments about this advisory, Amazon ECS asks that users contact [AWS/Amazon] Security via [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

### Acknowledgement

Amazon ECS would like to thank Sachin Patil for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/amazon-ecs-agent/security/advisories/GHSA-fc67-c4hg-q653
- https://github.com/aws/amazon-ecs-agent

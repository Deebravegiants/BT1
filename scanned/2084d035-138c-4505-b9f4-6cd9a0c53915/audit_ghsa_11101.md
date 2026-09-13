# [M] Improper S3 ownership verification in Bedrock AgentCore Starter Toolkit

## Summary
Severity: Medium
Advisory: GHSA-xfhr-q72q-jcrj
CVE: CVE-2026-4269
CWE: CWE-283, CWE-340
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-xfhr-q72q-jcrj
Type: github-advisory

## Affected
- PyPI: `bedrock-agentcore-starter-toolkit` — affected >=0 <0.1.13

## Details
## Summary
An issue has been identified in the Bedrock AgentCore Starter Toolkit versions prior to v0.1.13 that may allow a remote actor to inject code during the build process, leading to code execution in the AgentCore Runtime.


## Impact
A remote actor could inject code during the build process, leading to code execution in the AgentCore Runtime and a complete loss of confidentiality, integrity, and availability of the affected AgentCore resource.

Impacted versions:  All versions of Bedrock AgentCore Starter Toolkit versions before v0.1.13. This issue only affects users of the Bedrock AgentCore Starter Toolkit before version v0.1.13 who build the Toolkit after September 24, 2025. Any users on a version >=v0.1.13, and any users on previous versions who built the toolkit before September 24, 2025 date are not affected. 

## Patches
This issue has been addressed in version v0.1.13. AWS recommends upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

## Workarounds
N/A

## References
If you have any questions or comments about this advisory, contact [AWS/Amazon] Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/bedrock-agentcore-starter-toolkit/security/advisories/GHSA-xfhr-q72q-jcrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-4269
- https://aws.amazon.com/security/security-bulletins/2026-008-AWS
- https://github.com/aws/bedrock-agentcore-starter-toolkit
- https://github.com/aws/bedrock-agentcore-starter-toolkit/releases/tag/v0.1.13

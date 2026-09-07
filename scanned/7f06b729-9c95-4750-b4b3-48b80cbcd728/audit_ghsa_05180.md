# [H] Improper neutralization of argument delimiters in AWS Bedrock AgentCore Python SDK install_packages()

## Summary
Severity: High
Advisory: GHSA-6rfw-mq36-jm8h
CVE: CVE-2026-12530
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6rfw-mq36-jm8h
Type: github-advisory

## Affected
- PyPI: `bedrock-agentcore` — affected >=1.1.3 <1.6.1

## Details
### Summary
The AWS Bedrock AgentCore Python SDK (bedrock-agentcore) is an open-source SDK that enables developers to build, deploy, and manage agents on AWS Bedrock AgentCore. An issue exists in the install_packages() method of the Code Interpreter client where crafted package name arguments can bypass input validation and allow a remote authenticated user to execute arbitrary commands within the Code Interpreter sandbox.


### Impact
The install_packages() method constructs a 'pip install' shell command executed within the Code Interpreter sandbox using package name arguments provided by the caller. The method applied an incomplete blocklist that allowed crafted package name arguments - specifically pip flags such as '--index-url' and '-r' - to pass validation unchecked. A remote authenticated user who can influence the arguments passed to install_packages() could redirect package resolution to a third-party-controlled PyPI server, or expose the contents of arbitrary sandbox files and environment variables.

**Impacted versions:** AWS Bedrock AgentCore Python SDK (bedrock-agentcore) versions >= 1.1.3 and < 1.6.1

### Patches
This issue has been addressed in bedrock-agentcore version 1.6.1. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

### Workarounds
If you are unable to upgrade immediately, avoid passing any user-supplied or externally-influenced strings directly to install_packages(). Restrict calls to a fixed, hardcoded list of approved package names within your application code.

### References
If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.


We would like to thank Sergio Garcia for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/aws/bedrock-agentcore-sdk-python/security/advisories/GHSA-6rfw-mq36-jm8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-12530
- https://aws.amazon.com/security/security-bulletins/2026-044-aws
- https://github.com/aws/bedrock-agentcore-sdk-python
- https://pypi.org/project/bedrock-agentcore/1.6.1

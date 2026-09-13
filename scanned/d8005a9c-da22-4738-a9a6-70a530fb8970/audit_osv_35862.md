# [M] Sensitive content disclosure via OpenTelemetry spans in AgentCore Python SDK

## Summary
Severity: Medium
Advisory: CVE-2026-15737
Aliases: GHSA-hqf8-7w95-9r33
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-15737
Type: osv

## Details
AWS Bedrock AgentCore Python SDK is an open-source Python library that provides client tools for building AI agents on the Amazon Bedrock AgentCore platform.



Unintended logging of sensitive user content in the OpenTelemetry instrumentation in AWS Bedrock AgentCore Python SDK versions 1.4.8 and 1.5.0 might allow a local authenticated user with access to CloudWatch Logs to access raw user prompts and agent responses containing sensitive data via span attributes. The SDK wrote raw user prompts and complete agent responses into OpenTelemetry span attributes on every invocation without filtering or masking. These spans flow into the customer's aws/spans CloudWatch log group, exposing sensitive content to any principal with log read access.



We recommend you upgrade to version 1.5.1 or later. Users who ran affected versions should also review and purge sensitive content from their aws/spans CloudWatch log groups.

## References
- https://aws.amazon.com/security/security-bulletins/2026-058-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15737.json
- https://github.com/aws/bedrock-agentcore-sdk-python/security/advisories/GHSA-hqf8-7w95-9r33
- https://nvd.nist.gov/vuln/detail/CVE-2026-15737
- https://pypi.org/project/bedrock-agentcore/1.5.1/

# [M] Denial of Service due to Panic in AWS SDK for Go v2 SDK EventStream Decoder

## Summary
Severity: Medium
Advisory: GHSA-xmrv-pmrh-hhx2
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-xmrv-pmrh-hhx2
Type: github-advisory

## Affected
- Go: `github.com/aws/aws-sdk-go-v2/aws/protocol/eventstream` — affected >=0 <1.7.8
- Go: `github.com/aws/aws-sdk-go-v2/service/bedrockagentcore` — affected >=0 <1.15.2
- Go: `github.com/aws/aws-sdk-go-v2/service/bedrockagentruntime` — affected >=0 <1.51.8
- Go: `github.com/aws/aws-sdk-go-v2/service/bedrockruntime` — affected >=0 <1.50.4
- Go: `github.com/aws/aws-sdk-go-v2/service/cloudwatchlogs` — affected >=0 <1.65.0
- Go: `github.com/aws/aws-sdk-go-v2/service/iotsitewise` — affected >=0 <1.52.19
- Go: `github.com/aws/aws-sdk-go-v2/service/kinesis` — affected >=0 <1.43.5
- Go: `github.com/aws/aws-sdk-go-v2/service/lambda` — affected >=0 <1.88.5
- Go: `github.com/aws/aws-sdk-go-v2/service/lexruntimev2` — affected >=0 <1.35.15
- Go: `github.com/aws/aws-sdk-go-v2/service/s3` — affected >=0 <1.97.3
- Go: `github.com/aws/aws-sdk-go-v2/service/sagemakerruntime` — affected >=0 <1.39.6
- Go: `github.com/aws/aws-sdk-go-v2/service/transcribestreaming` — affected >=0 <1.34.5

## Details
**CVSSv3.1 Rating**: [Medium]
**CVSSv3.1 Score**: [5.9]
**CVSSv3.1 Vector String**: [CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H]

## Summary and Impact
An issue exists in the the EventStream header decoder in AWS SDK for Go v2 in versions predating [2026-03-23](https://github.com/aws/aws-sdk-go-v2/releases/tag/release-2026-03-23). An actor can send a malformed EventStream response frame containing a crafted header value type byte outside the valid range, which can cause the host process to terminate.

Impacted versions: < [2026-03-23](https://github.com/aws/aws-sdk-go-v2/releases/tag/release-2026-03-23)

## Patches
This issue has been addressed in versions [2026-03-23](https://github.com/aws/aws-sdk-go-v2/releases/tag/release-2026-03-23) and above. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes. 

## Workarounds
Not Applicable

## References
If you have any questions or comments about this advisory, we ask that you contact [AWS/Amazon] Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/aws-sdk-go-v2/security/advisories/GHSA-xmrv-pmrh-hhx2
- https://github.com/aws/aws-sdk-go-v2
- https://github.com/aws/aws-sdk-go-v2/releases/tag/release-2026-03-23

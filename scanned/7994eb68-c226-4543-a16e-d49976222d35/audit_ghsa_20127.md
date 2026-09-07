# [H] Amazon CloudWatch Agent for Windows has Privilege Escalation Vector

## Summary
Severity: High
Advisory: GHSA-j8x2-2m5w-j939
CVE: CVE-2022-23511
CWE: CWE-274
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-j8x2-2m5w-j939
Type: github-advisory

## Affected
- Go: `github.com/aws/amazon-cloudwatch-agent` — affected >=0 <1.247355.0

## Details
### Impact
A privilege escalation issue exists within the Amazon CloudWatch Agent for Windows in versions up to and including v1.247354. When users trigger a repair of the Agent, a pop-up window opens with SYSTEM permissions. Users with administrative access to affected hosts may use this to create a new command prompt as NT AUTHORITY\SYSTEM. 
 
To trigger this issue, the third party must be able to access the affected host and elevate their privileges such that they’re able to trigger the agent repair process. They must also be able to install the tools required to trigger the issue. 

This issue does not affect the CloudWatch Agent for macOS or Linux. 

### Patches
Maintainers recommend that Agent users upgrade to the latest available version of the CloudWatch Agent to address this issue. 

### Workarounds
There is no recommended work around. Affected users must update the installed version of the CloudWatch Agent to address this issue.

### References
https://github.com/aws/amazon-cloudwatch-agent/commit/6119858864c317ff26f41f576c169148d1250837

### For more information 
 
If you have any questions or comments about this advisory, contact AWS/Amazon Security via their [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/aws/amazon-cloudwatch-agent/security/advisories/GHSA-j8x2-2m5w-j939
- https://nvd.nist.gov/vuln/detail/CVE-2022-23511
- https://github.com/aws/amazon-cloudwatch-agent/commit/6119858864c317ff26f41f576c169148d1250837
- https://github.com/aws/amazon-cloudwatch-agent/commit/6119858864c317ff26f41f576c169148d1250837#diff-76ed074a9305c04054cdebb9e9aad2d818052b07091de1f20cad0bbac34ffb52
- https://github.com/aws/amazon-cloudwatch-agent

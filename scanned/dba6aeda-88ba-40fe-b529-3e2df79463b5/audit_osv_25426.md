# [H] AWS data.all vulnerable to RCE through user injection of Python Commands

## Summary
Severity: High
Advisory: CVE-2023-36467
Aliases: GHSA-m922-chh7-8qcr
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-36467
Type: osv

## Details
AWS data.all is an open source development framework to help users build a data marketplace on Amazon Web Services. data.all versions 1.2.0 through 1.5.1 do not prevent remote code execution when a user injects Python commands into the ‘Template’ field when configuring a data pipeline. The issue can only be triggered by authenticated users. A fix for this issue is available in data.all version 1.5.2 and later. There is no recommended work around.

## References
- https://github.com/awslabs/aws-dataall/releases/tag/v1.5.2
- https://github.com/awslabs/aws-dataall/releases/tag/v1.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36467.json
- https://github.com/awslabs/aws-dataall/security/advisories/GHSA-m922-chh7-8qcr
- https://nvd.nist.gov/vuln/detail/CVE-2023-36467
- https://github.com/awslabs/aws-dataall/pull/472

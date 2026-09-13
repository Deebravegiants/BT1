# [M] JumpServer Koko vulnerable to Command Injection for Kubernetes Connection

## Summary
Severity: Medium
Advisory: CVE-2023-28110
Aliases: GHSA-6x5p-jm59-jh29
CVSS: 5.7 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:H)
Published: 2023-03-16
Source: https://osv.dev/vulnerability/CVE-2023-28110
Type: osv

## Details
Jumpserver is a popular open source bastion host, and Koko is a Jumpserver component that is the Go version of coco, refactoring coco's SSH/SFTP service and Web Terminal service. Prior to version 2.28.8, using illegal tokens to connect to a Kubernetes cluster through Koko can result in the execution of dangerous commands that may disrupt the Koko container environment and affect normal usage. The vulnerability has been fixed in v2.28.8.

## References
- https://github.com/jumpserver/jumpserver/releases/tag/v2.28.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28110.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-6x5p-jm59-jh29
- https://nvd.nist.gov/vuln/detail/CVE-2023-28110

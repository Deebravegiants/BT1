# [M] Server-side request forgery in the Session Manager port forwarding functionality in AWS Systems Manager Agent

## Summary
Severity: Medium
Advisory: CVE-2026-89049
Aliases: GHSA-w9jw-h72g-6hxc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-89049
Type: osv

## Details
A server-side request forgery issue due to improper validation of equivalent address representations in the port forwarding to remote hosts functionality in Amazon AWS Systems Manager Agent (SSM Agent) before 3.3.4851.0 on all platforms might allow an authenticated remote user to bypass the remote destination denylist and reach link-local endpoints, potentially obtaining the temporary IAM role credentials of a managed instance and acting with that role's permissions from outside the instance, via a crafted destination host value that uses an alternate representation of a denied link-local address.



To remediate this issue, users should upgrade to version 3.3.4851.0 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-107-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89049.json
- https://github.com/aws/amazon-ssm-agent/security/advisories/GHSA-w9jw-h72g-6hxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-89049
- https://github.com/aws/amazon-ssm-agent/releases/tag/3.3.4851.0

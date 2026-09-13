# [C] Improper Control of User-Modifiable Attributes in RES CreateSession API

## Summary
Severity: Critical
Advisory: CVE-2026-5708
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-5708
Type: osv

## Details
Unsanitized control of user-modifiable attributes in the session creation component in AWS Research and Engineering Studio (RES) prior to version 2026.03 could allow an authenticated remote user to escalate privileges, assume the virtual desktop host instance profile permissions, and interact with AWS resources and services via a crafted API request.

To remediate this issue, users are advised to upgrade to RES version 2026.03 or apply the corresponding mitigation patch to their existing environment.

## References
- https://aws.amazon.com/security/security-bulletins/2026-014-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5708.json
- https://github.com/aws/res/releases/tag/2026.03
- https://nvd.nist.gov/vuln/detail/CVE-2026-5708
- https://github.com/aws/res/issues/149

# [C] Command Injection via Virtual Desktop Session Name in AWS Research and Engineering Studio (RES)

## Summary
Severity: Critical
Advisory: CVE-2026-5707
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-5707
Type: osv

## Details
Unsanitized input in an OS command in the virtual desktop session name handling in AWS Research and Engineering Studio (RES) version 2025.03 through 2025.12.01 might allow a remote authenticated actor to execute arbitrary commands as root on the virtual desktop host via a crafted session name.

To remediate this issue, users are advised to upgrade to RES version 2026.03 or apply the corresponding mitigation patch to their existing environment.

## References
- https://aws.amazon.com/security/security-bulletins/2026-014-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5707.json
- https://github.com/aws/res/releases/tag/2026.03
- https://nvd.nist.gov/vuln/detail/CVE-2026-5707
- https://github.com/aws/res/issues/151

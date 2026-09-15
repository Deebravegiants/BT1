# [M] RES Auth.GetUserPrivateKey Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-14904
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-14904
Type: osv

## Details
AWS Research and Engineering Studio (RES) is an open-source solution that enables researchers and engineers to create and manage secure virtual desktops and computing resources on AWS.



Improper link resolution before file access issue (CWE-59) in the Auth.GetUserPrivateKey API. An authenticated remote user could read arbitrary files on the cluster-manager EC2 instance by replacing their SSH private key file (~/.ssh/id_rsa) with a symbolic link targeting any file on the host. Because the cluster-manager process runs as root, any file readable by root is exposed, including other users' SSH private keys and application configuration secrets.



It's recommended to upgrade to RES version 2026.06.

## References
- https://aws.amazon.com/security/security-bulletins/2026-053-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14904.json
- https://github.com/aws/res/releases/tag/2026.06
- https://nvd.nist.gov/vuln/detail/CVE-2026-14904

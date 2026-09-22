# [C] Creation of Temporary File in Directory with Insecure Permissions in AWS FPGA Development Kit

## Summary
Severity: Critical
Advisory: CVE-2026-85028
Aliases: GHSA-g4hc-wrmm-2x74
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85028
Type: osv

## Details
Creation of a temporary file in a directory with insecure permissions in the FPGA management tool installation component in AWS FPGA Development Kit (aws-fpga) before 2.3.4 might allow local users to execute arbitrary code with root privileges via crafted shell content placed at a predictable path in a world-writable temporary directory, which the installation step reads after elevating its own privileges.



To remediate this issue, users should upgrade to version 2.3.4.

## References
- https://aws.amazon.com/security/security-bulletins/2026-096-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85028.json
- https://github.com/aws/aws-fpga/security/advisories/GHSA-g4hc-wrmm-2x74
- https://nvd.nist.gov/vuln/detail/CVE-2026-85028
- https://github.com/aws/aws-fpga/releases/tag/v2.3.4

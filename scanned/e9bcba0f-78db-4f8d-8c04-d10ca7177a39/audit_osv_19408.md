# [C] CVE-2021-21244

## Summary
Severity: Critical
Advisory: CVE-2021-21244
Aliases: GHSA-vm26-xg39-cfj4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21244
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, There is a vulnerability that enabled pre-auth server side template injection via Bean validation message tampering. Full details in the reference GHSA. This issue was fixed in 4.0.3 by disabling validation interpolation completely.

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-vm26-xg39-cfj4
- https://github.com/theonedev/onedev/commit/4f5dc6fb9e50f2c41c4929b0d8c5824b2cca3d65

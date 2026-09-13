# [C] CVE-2025-63691

## Summary
Severity: Critical
Advisory: CVE-2025-63691
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-63691
Type: osv

## Details
In pig-mesh In Pig version 3.8.2 and below, within the Token Management function under the System Management module, the token query interface (/api/admin/sys-token/page) has an improper permission verification issue, which leads to information leakage. This interface can be called by any user who has completed login authentication, and it returns the plaintext authentication Tokens of all users currently logged in to the system. As a result, ordinary users can obtain the administrator's authentication Token through this interface, thereby forging an administrator account, gaining the system's management permissions, and taking over the system.

## References
- https://github.com/LockeTom/vulnerability/blob/main/md/pig_Information_disclosure_vulnerability.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63691.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63691
- https://github.com/pig-mesh/pig/issues/1202

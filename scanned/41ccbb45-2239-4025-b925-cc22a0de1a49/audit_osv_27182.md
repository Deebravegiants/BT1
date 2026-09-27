# [M] Access Control Vulnerabilities Allow Unauthorized Access to User Profiles in Unifiedtransform

## Summary
Severity: Medium
Advisory: CVE-2024-12306
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-12306
Type: osv

## Details
Multiple access control vulnerabilities in Unifiedtransform version 2.0 and potentially earlier versions allow unauthorized access to personal information of students and teachers. The vulnerabilities include both function-level access control issues in list viewing endpoints and object-level access control issues in profile viewing endpoints. A malicious student user can access personal information of other students and teachers through these vulnerabilities. At the time of publication of the CVE no patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12306.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12306
- https://github.com/changeweb/Unifiedtransform
- https://huntr.com/bounties/90a7299e-9233-43fd-b666-7375c4fdbb3c

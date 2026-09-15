# [C] Mingsoft MCMS vulnerable to Remote Code Execution via file upload.

## Summary
Severity: Critical
Advisory: GHSA-cwx9-rp4w-4545
CVE: CVE-2021-46386
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-cwx9-rp4w-4545
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
Mingsoft MCMS is a Java CMS. Versions prior to and including 5.2.5 contain a file upload vulnerability allowing for a jspx webshell to be uploaded via net.mingsoft.basic.action.web.FileAction#upload, resulting in remote code execution. It is unclear if this issue has been patched.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46386
- https://gitee.com/mingSoft/MCMS
- https://gitee.com/mingSoft/MCMS/issues/I4R0GW
- https://github.com/ming-soft/MCMS

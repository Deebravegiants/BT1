# [C] CVE-2024-24000

## Summary
Severity: Critical
Advisory: CVE-2024-24000
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-24000
Type: osv

## Details
jshERP v3.3 is vulnerable to Arbitrary File Upload. The jshERP-boot/systemConfig/upload interface does not check the uploaded file type, and the biz parameter can be spliced into the upload path, resulting in arbitrary file uploads with controllable paths.

## References
- https://github.com/cxcxcxcxcxcxcxc/cxcxcxcxcxcxcxc/blob/main/cxcxcxcxcxc/about-2024/24000.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24000.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24000
- https://github.com/jishenghua/jshERP

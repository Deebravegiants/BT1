# [M] Arbitrary File Read in Fusion File Manager

## Summary
Severity: Medium
Advisory: CVE-2023-4480
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-4480
Type: osv

## Details
Due to an out-of-date dependency in the “Fusion File Manager” component accessible through the admin panel, an attacker can send a crafted request that allows them to read the contents of files on the system accessible within the privileges of the running process. Additionally, they may write files to arbitrary locations, provided the files pass the application’s mime-type and file extension validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4480.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4480
- https://www.synopsys.com/blogs/software-security/cyrc-vulnerability-advisory-cve-2023-2453/
- https://github.com/PHPFusion/PHPFusion

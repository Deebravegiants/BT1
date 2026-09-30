# [H] CVE-2022-46604

## Summary
Severity: High
Advisory: CVE-2022-46604
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-02
Source: https://osv.dev/vulnerability/CVE-2022-46604
Type: osv

## Details
An issue in Tecrail Responsive FileManager v9.9.5 and below allows attackers to bypass the file extension check mechanism and upload a crafted PHP file, leading to arbitrary code execution.

## References
- http://packetstormsecurity.com/files/171720/Responsive-FileManager-9.9.5-Remote-Shell-Upload.html
- https://github.com/trippo/ResponsiveFilemanager/blob/v9.9.5/filemanager/execute.php
- https://github.com/trippo/ResponsiveFilemanager/blob/v9.9.6/changelog.txt
- https://medium.com/%40_sadshade/file-extention-bypass-in-responsive-filemanager-9-5-5-leading-to-rce-authenticated-3290eddc54e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46604.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46604

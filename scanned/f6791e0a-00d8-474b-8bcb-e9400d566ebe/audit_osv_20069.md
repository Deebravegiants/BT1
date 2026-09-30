# [M] CVE-2021-30048

## Summary
Severity: Medium
Advisory: CVE-2021-30048
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-30048
Type: osv

## Details
Directory Traversal in the fileDownload function in com/java2nb/common/controller/FileController.java in Novel-plus (小说精品屋-plus) 3.5.1 allows attackers to read arbitrary files via the filePath parameter.

## References
- https://github.com/201206030/novel-plus/issues/39
- https://www.exploit-db.com/exploits/49724

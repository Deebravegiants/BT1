# [H] CVE-2018-9037

## Summary
Severity: High
Advisory: CVE-2018-9037
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-10
Source: https://osv.dev/vulnerability/CVE-2018-9037
Type: osv

## Details
Monstra CMS 3.0.4 allows remote code execution via an upload_file request for a .zip file, which is automatically extracted and may contain .php files.

## References
- https://www.exploit-db.com/exploits/44621/
- https://github.com/monstra-cms/monstra/issues/433

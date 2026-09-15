# [C] CVE-2016-10752

## Summary
Severity: Critical
Advisory: CVE-2016-10752
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-24
Source: https://osv.dev/vulnerability/CVE-2016-10752
Type: osv

## Details
serendipity_moveMediaDirectory in Serendipity 2.0.3 allows remote attackers to upload and execute arbitrary PHP code because it mishandles an extensionless filename during a rename, as demonstrated by "php" as a filename.

## References
- https://blog.ripstech.com/2016/serendipity-from-file-upload-to-code-execution/
- https://demo.ripstech.com/projects/serendipity_2.0.3

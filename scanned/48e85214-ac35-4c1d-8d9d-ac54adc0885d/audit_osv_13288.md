# [H] CVE-2018-19114

## Summary
Severity: High
Advisory: CVE-2018-19114
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19114
Type: osv

## Details
An issue was discovered in MinDoc through v1.0.2. It allows attackers to gain privileges by uploading an image file with contents that represent an admin session, and then sending a Cookie: header with a mindoc_id value containing the relative pathname of this uploaded file. For example, the mindoc_id (aka session ID) could be of the form aa/../../uploads/blog/201811/attach_#.jpg where '#' is a hex value displayed in the upload field of a manage/blogs/edit/ screen.

## References
- https://github.com/lifei6671/mindoc/issues/384

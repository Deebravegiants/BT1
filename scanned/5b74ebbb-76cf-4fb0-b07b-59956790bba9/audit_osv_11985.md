# [H] CVE-2018-1000535

## Summary
Severity: High
Advisory: CVE-2018-1000535
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000535
Type: osv

## Details
lms version <= LMS_011123 contains a Local File Disclosure vulnerability in File reading functionality in LMS module that can result in Possible to read files on the server. This attack appear to be exploitable via GET parameter. This vulnerability appears to have been fixed in after commit 254765e.

## References
- https://0dd.zone/2018/06/01/LMS-Local-File-Disclosure/
- https://github.com/lmsgit/lms/issues/1271

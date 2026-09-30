# [M] CVE-2018-11762

## Summary
Severity: Medium
Advisory: CVE-2018-11762
Aliases: GHSA-w6g3-v46q-5p28
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-11762
Type: osv

## Details
In Apache Tika 0.9 to 1.18, in a rare edge case where a user does not specify an extract directory on the commandline (--extract-dir=) and the input file has an embedded file with an absolute path, such as "C:/evil.bat", tika-app would overwrite that file.

## References
- https://lists.apache.org/thread.html/ab2e1af38975f5fc462ba89b517971ef892ec3d06bee12ea2258895b%40%3Cdev.tika.apache.org%3E
- http://www.securityfocus.com/bid/105515

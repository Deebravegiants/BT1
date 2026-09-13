# [H] CVE-2017-5480

## Summary
Severity: High
Advisory: CVE-2017-5480
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-01-15
Source: https://osv.dev/vulnerability/CVE-2017-5480
Type: osv

## Details
Directory traversal vulnerability in inc/files/files.ctrl.php in b2evolution through 6.8.3 allows remote authenticated users to read or delete arbitrary files by leveraging back-office access to provide a .. (dot dot) in the fm_selected array parameter.

## References
- http://www.securityfocus.com/bid/95454
- https://github.com/b2evolution/b2evolution/issues/35
- https://github.com/b2evolution/b2evolution/commit/26841d9c81f27ad23b2f6e4bd5eaec7f2f58dfe0

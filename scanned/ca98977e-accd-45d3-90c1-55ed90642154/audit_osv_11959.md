# [H] CVE-2018-1000208

## Summary
Severity: High
Advisory: CVE-2018-1000208
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-1000208
Type: osv

## Details
MODX Revolution version <=2.6.4 contains a Directory Traversal vulnerability in /core/model/modx/modmanagerrequest.class.php that can result in remove files. This attack appear to be exploitable via web request via security/login processor. This vulnerability appears to have been fixed in pull 13980.

## References
- https://github.com/modxcms/revolution/pull/13980

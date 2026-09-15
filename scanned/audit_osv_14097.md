# [H] CVE-2018-7187

## Summary
Severity: High
Advisory: CVE-2018-7187
Aliases: GO-2022-0203
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-16
Source: https://osv.dev/vulnerability/CVE-2018-7187
Type: osv

## Details
The "go get" implementation in Go 1.9.4, when the -insecure command-line option is used, does not validate the import path (get/vcs.go only checks for "://" anywhere in the string), which allows remote attackers to execute arbitrary OS commands via a crafted web site.

## References
- https://gist.github.com/SLAYEROWNER/b2a358f13ab267f2e9543bb9f9320ffc
- https://lists.debian.org/debian-lts-announce/2018/02/msg00029.html
- https://security.gentoo.org/glsa/201804-12
- https://www.debian.org/security/2019/dsa-4379
- https://www.debian.org/security/2019/dsa-4380
- https://github.com/golang/go/issues/23867

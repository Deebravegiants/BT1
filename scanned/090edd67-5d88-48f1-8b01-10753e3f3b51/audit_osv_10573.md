# [H] CVE-2017-17405

## Summary
Severity: High
Advisory: CVE-2017-17405
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-15
Source: https://osv.dev/vulnerability/CVE-2017-17405
Type: osv

## Details
Ruby before 2.4.3 allows Net::FTP command injection. Net::FTP#get, getbinaryfile, gettextfile, put, putbinaryfile, and puttextfile use Kernel#open to open a local file. If the localfile argument starts with the "|" pipe character, the command following the pipe character is executed. The default value of localfile is File.basename(remotefile), so malicious FTP servers could cause arbitrary command execution.

## References
- http://www.securityfocus.com/bid/102204
- http://www.securitytracker.com/id/1042004
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0584
- https://access.redhat.com/errata/RHSA-2018:0585
- https://access.redhat.com/errata/RHSA-2019:2806
- https://lists.debian.org/debian-lts-announce/2017/12/msg00024.html
- https://lists.debian.org/debian-lts-announce/2017/12/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://www.debian.org/security/2018/dsa-4259
- https://www.ruby-lang.org/en/news/2017/12/14/net-ftp-command-injection-cve-2017-17405/
- https://www.ruby-lang.org/en/news/2017/12/14/ruby-2-4-3-released/
- https://www.exploit-db.com/exploits/43381/

# [H] CVE-2019-16255

## Summary
Severity: High
Advisory: CVE-2019-16255
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-16255
Type: osv

## Details
Ruby through 2.4.7, 2.5.x through 2.5.6, and 2.6.x through 2.6.4 allows code injection if the first argument (aka the "command" argument) to Shell#[] or Shell#test in lib/shell.rb is untrusted data. An attacker can exploit this to call an arbitrary Ruby method.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/11/msg00025.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00009.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00027.html
- https://seclists.org/bugtraq/2019/Dec/31
- https://seclists.org/bugtraq/2019/Dec/32
- https://security.gentoo.org/glsa/202003-06
- https://www.debian.org/security/2019/dsa-4587
- https://www.ruby-lang.org/ja/news/2019/10/01/code-injection-shell-test-cve-2019-16255/
- https://www.ruby-lang.org/ja/news/2019/10/01/ruby-2-4-8-released/
- https://www.ruby-lang.org/ja/news/2019/10/01/ruby-2-5-7-released/
- https://www.ruby-lang.org/ja/news/2019/10/01/ruby-2-6-5-released/
- https://hackerone.com/reports/327512
- https://www.oracle.com/security-alerts/cpujan2020.html

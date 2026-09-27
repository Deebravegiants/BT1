# [H] BIT-ruby-2022-28739

## Summary
Severity: High
Advisory: BIT-ruby-2022-28739
Aliases: BIT-ruby-min-2022-28739, CVE-2022-28739
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ruby-2022-28739
Type: osv

## Affected
- Bitnami: `ruby` — affected >=3.1.0 <3.1.2

## Details
There is a buffer over-read in Ruby before 2.6.10, 2.7.x before 2.7.6, 3.x before 3.0.4, and 3.1.x before 3.1.2. It occurs in String-to-Float conversion, including Kernel#Float and String#to_f.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/29
- http://seclists.org/fulldisclosure/2022/Oct/30
- http://seclists.org/fulldisclosure/2022/Oct/41
- http://seclists.org/fulldisclosure/2022/Oct/42
- https://hackerone.com/reports/1248108
- https://lists.debian.org/debian-lts-announce/2023/06/msg00012.html
- https://security-tracker.debian.org/tracker/CVE-2022-28739
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20220624-0002/
- https://support.apple.com/kb/HT213488
- https://support.apple.com/kb/HT213493
- https://support.apple.com/kb/HT213494
- https://www.ruby-lang.org/en/news/2022/04/12/buffer-overrun-in-string-to-float-cve-2022-28739/
- https://nvd.nist.gov/vuln/detail/CVE-2022-28739
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html

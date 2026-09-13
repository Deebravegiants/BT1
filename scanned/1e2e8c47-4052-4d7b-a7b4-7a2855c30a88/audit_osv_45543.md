# [H] JLSEC-2026-1290

## Summary
Severity: High
Advisory: JLSEC-2026-1290
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1290
Type: osv

## Affected
- Julia: `ruby_jll` — affected unspecified

## Details
There is a buffer over-read in Ruby before 2.6.10, 2.7.x before 2.7.6, 3.x before 3.0.4, and 3.1.x before 3.1.2. It occurs in String-to-Float conversion, including Kernel#Float and String#`to_f`.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/29
- http://seclists.org/fulldisclosure/2022/Oct/29
- http://seclists.org/fulldisclosure/2022/Oct/30
- http://seclists.org/fulldisclosure/2022/Oct/30
- http://seclists.org/fulldisclosure/2022/Oct/41
- http://seclists.org/fulldisclosure/2022/Oct/41
- http://seclists.org/fulldisclosure/2022/Oct/42
- http://seclists.org/fulldisclosure/2022/Oct/42
- https://hackerone.com/reports/1248108
- https://hackerone.com/reports/1248108
- https://lists.debian.org/debian-lts-announce/2023/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00000.html
- https://security-tracker.debian.org/tracker/CVE-2022-28739
- https://security-tracker.debian.org/tracker/CVE-2022-28739
- https://security.gentoo.org/glsa/202401-27
- https://security.gentoo.org/glsa/202401-27
- https://security.netapp.com/advisory/ntap-20220624-0002/

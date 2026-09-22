# [H] JLSEC-2026-391

## Summary
Severity: High
Advisory: JLSEC-2026-391
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-391
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.83.1+0

## Details
libcurl would reuse a previously created connection even when a TLS or SSHrelated option had been changed that should have prohibited reuse.libcurl keeps previously used connections in a connection pool for subsequenttransfers to reuse if one of them matches the setup. However, several TLS andSSH settings were left out from the configuration match checks, making themmatch too easily.

## References
- http://www.openwall.com/lists/oss-security/2023/03/20/6
- https://hackerone.com/reports/1555796
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220609-0009/
- https://www.debian.org/security/2022/dsa-5197

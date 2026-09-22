# [M] JLSEC-2026-395

## Summary
Severity: Medium
Advisory: JLSEC-2026-395
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-395
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.84.0+0

## Details
When curl < 7.84.0 does FTP transfers secured by krb5, it handles message verification failures wrongly. This flaw makes it possible for a Man-In-The-Middle attack to go unnoticed and even allows it to inject data to the client.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://hackerone.com/reports/1590071
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEV6BR4MTI3CEWK2YU2HQZUW5FAS3FEY/
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220915-0003/
- https://support.apple.com/kb/HT213488
- https://www.debian.org/security/2022/dsa-5197

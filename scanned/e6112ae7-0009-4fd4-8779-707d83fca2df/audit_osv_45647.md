# [H] JLSEC-2026-161

## Summary
Severity: High
Advisory: JLSEC-2026-161
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/JLSEC-2026-161
Type: osv

## Affected
- Julia: `OpenLDAPClient_jll` — affected >=0 <2.5.14+0

## Details
A flaw was found in OpenLDAP. This flaw allows an attacker who can send a malicious packet to be processed by OpenLDAP’s slapd server, to trigger an assertion failure. The highest threat from this vulnerability is to system availability.

## References
- http://seclists.org/fulldisclosure/2021/Feb/14
- https://bugzilla.redhat.com/show_bug.cgi?id=1899675
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00008.html
- https://security.netapp.com/advisory/ntap-20210716-0003/
- https://support.apple.com/kb/HT212147
- https://www.debian.org/security/2020/dsa-4792

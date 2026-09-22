# [H] JLSEC-2026-405

## Summary
Severity: High
Advisory: JLSEC-2026-405
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-405
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.0.1+0

## Details
A vulnerability in input validation exists in curl <8.0 during communication using the TELNET protocol may allow an attacker to pass on maliciously crafted user name and "telnet options" during server negotiation. The lack of proper input scrubbing allows an attacker to send content or perform option negotiation without the application's intent. This vulnerability could be exploited if an application allows user input, thereby enabling attackers to execute arbitrary code on the system.

## References
- https://hackerone.com/reports/1891474
- https://lists.debian.org/debian-lts-announce/2023/04/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36NBD5YLJXXEDZLDGNFCERWRYJQ6LAQW/
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0011/

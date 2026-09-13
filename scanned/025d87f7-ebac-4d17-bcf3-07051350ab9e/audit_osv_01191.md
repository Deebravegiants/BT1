# [H] ALPINE-CVE-2018-5336

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5336
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5336
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.12-r0

## Details
In Wireshark 2.4.0 to 2.4.3 and 2.2.0 to 2.2.11, the JSON, XML, NTP, XMPP, and GDB dissectors could crash. This was addressed in epan/tvbparse.c by limiting the recursion depth.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5336

# [H] ALPINE-CVE-2017-7703

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7703
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7703
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=0 <2.2.6-r0

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the IMAP dissector could crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-imap.c by calculating a line's end correctly.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7703

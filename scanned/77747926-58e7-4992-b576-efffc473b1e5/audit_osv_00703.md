# [H] ALPINE-CVE-2017-6469

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6469
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6469
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.0.0 <2.2.5-r0

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is an LDSS dissector crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-ldss.c by ensuring that memory is allocated for a certain data structure.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6469

# [H] ALPINE-CVE-2017-9352

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9352
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9352
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.0.0 <2.2.7-r0

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the Bazaar dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-bzr.c by ensuring that backwards parsing cannot occur.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9352

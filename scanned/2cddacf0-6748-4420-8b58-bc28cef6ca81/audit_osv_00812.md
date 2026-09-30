# [H] ALPINE-CVE-2017-9343

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9343
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9343
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.0.0 <2.2.7-r0

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the MSNIP dissector misuses a NULL pointer. This was addressed in epan/dissectors/packet-msnip.c by validating an IPv4 address.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9343

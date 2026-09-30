# [H] ALPINE-CVE-2017-9348

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9348
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9348
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.7-r0

## Details
In Wireshark 2.2.0 to 2.2.6, the DOF dissector could read past the end of a buffer. This was addressed in epan/dissectors/packet-dof.c by validating a size value.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9348

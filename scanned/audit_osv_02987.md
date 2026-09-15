# [H] ALPINE-CVE-2024-1580

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-1580
Ecosystem: Alpine:v3.19
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-1580
Type: osv

## Affected
- Alpine:v3.19: `dav1d` — affected >=0 <1.3.0-r1

## Details
An integer overflow in dav1d AV1 decoder that can occur when decoding videos with large frame size. This can lead to memory corruption within the AV1 decoder. We recommend upgrading past version 1.4.0 of dav1d.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-1580

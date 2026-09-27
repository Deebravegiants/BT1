# [C] ALPINE-CVE-2019-17362

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-17362
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17362
Type: osv

## Affected
- Alpine:v3.19: `perl-cryptx` — affected >=0 <0.079-r0
- Alpine:v3.20: `perl-cryptx` — affected >=0 <0.079-r0
- Alpine:v3.21: `perl-cryptx` — affected >=0 <0.079-r0
- Alpine:v3.22: `perl-cryptx` — affected >=0 <0.079-r0
- Alpine:v3.23: `perl-cryptx` — affected >=0 <0.079-r0
- Alpine:v3.24: `perl-cryptx` — affected >=0 <0.079-r0

## Details
In LibTomCrypt through 1.18.2, the der_decode_utf8_string function (in der_decode_utf8_string.c) does not properly detect certain invalid UTF-8 sequences. This allows context-dependent attackers to cause a denial of service (out-of-bounds read and crash) or read information from other memory locations via carefully crafted DER-encoded data.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17362

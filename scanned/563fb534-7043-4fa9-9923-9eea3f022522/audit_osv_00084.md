# [H] ALPINE-CVE-2016-2181

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2181
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2181
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r4
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r4
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r4
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r4
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r4
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r4
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r4

## Details
The Anti-Replay feature in the DTLS implementation in OpenSSL before 1.1.0 mishandles early use of a new epoch number in conjunction with a large sequence number, which allows remote attackers to cause a denial of service (false-positive packet drops) via spoofed DTLS records, related to rec_layer_d1.c and ssl3_record.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2181

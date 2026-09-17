# [C] ALPINE-CVE-2026-31789

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-31789
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-31789
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.3.7-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.3.7-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.5.6-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.5.6-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.5.6-r0

## Details
Issue summary: Converting an excessively large OCTET STRING value to
a hexadecimal string leads to a heap buffer overflow on 32 bit platforms.

Impact summary: A heap buffer overflow may lead to a crash or possibly
an attacker controlled code execution or other undefined behavior.

If an attacker can supply a crafted X.509 certificate with an excessively
large OCTET STRING value in extensions such as the Subject Key Identifier
(SKID) or Authority Key Identifier (AKID) which are being converted to hex,
the size of the buffer needed for the result is calculated as multiplication
of the input length by 3. On 32 bit platforms, this multiplication may overflow
resulting in the allocation of a smaller buffer and a heap buffer overflow.

Applications and services that print or log contents of untrusted X.509
certificates are vulnerable to this issue. As the certificates would have
to have sizes of over 1 Gigabyte, printing or logging such certificates
is a fairly unlikely operation and only 32 bit platforms are affected,
this issue was assigned Low severity.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-31789

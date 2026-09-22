# [H] ALPINE-CVE-2025-69419

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-69419
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-69419
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.1.1 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.5.5-r0

## Details
Issue summary: Calling PKCS12_get_friendlyname() function on a maliciously
crafted PKCS#12 file with a BMPString (UTF-16BE) friendly name containing
non-ASCII BMP code point can trigger a one byte write before the allocated
buffer.

Impact summary: The out-of-bounds write can cause a memory corruption
which can have various consequences including a Denial of Service.

The OPENSSL_uni2utf8() function performs a two-pass conversion of a PKCS#12
BMPString (UTF-16BE) to UTF-8. In the second pass, when emitting UTF-8 bytes,
the helper function bmp_to_utf8() incorrectly forwards the remaining UTF-16
source byte count as the destination buffer capacity to UTF8_putc(). For BMP
code points above U+07FF, UTF-8 requires three bytes, but the forwarded
capacity can be just two bytes. UTF8_putc() then returns -1, and this negative
value is added to the output length without validation, causing the
length to become negative. The subsequent trailing NUL byte is then written
at a negative offset, causing write outside of heap allocated buffer.

The vulnerability is reachable via the public PKCS12_get_friendlyname() API
when parsing attacker-controlled PKCS#12 files. While PKCS12_parse() uses a
different code path that avoids this issue, PKCS12_get_friendlyname() directly
invokes the vulnerable function. Exploitation requires an attacker to provide
a malicious PKCS#12 file to be parsed by the application and the attacker
can just trigger a one zero byte write before the allocated buffer.
For that reason the issue was assessed as Low severity according to our
Security Policy.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS#12 implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0 and 1.1.1 are vulnerable to this issue.

OpenSSL 1.0.2 is not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-69419

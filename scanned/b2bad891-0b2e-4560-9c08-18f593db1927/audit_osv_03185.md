# [M] ALPINE-CVE-2025-11187

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-11187
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-11187
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.4.0 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=3.4.0 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=3.4.0 <3.5.5-r0

## Details
Issue summary: PBMAC1 parameters in PKCS#12 files are missing validation
which can trigger a stack-based buffer overflow, invalid pointer or NULL
pointer dereference during MAC verification.

Impact summary: The stack buffer overflow or NULL pointer dereference may
cause a crash leading to Denial of Service for an application that parses
untrusted PKCS#12 files. The buffer overflow may also potentially enable
code execution depending on platform mitigations.

When verifying a PKCS#12 file that uses PBMAC1 for the MAC, the PBKDF2
salt and keylength parameters from the file are used without validation.
If the value of keylength exceeds the size of the fixed stack buffer used
for the derived key (64 bytes), the key derivation will overflow the buffer.
The overflow length is attacker-controlled. Also, if the salt parameter is
not an OCTET STRING type this can lead to invalid or NULL pointer
dereference.

Exploiting this issue requires a user or application to process
a maliciously crafted PKCS#12 file. It is uncommon to accept untrusted
PKCS#12 files in applications as they are usually used to store private
keys which are trusted by definition. For this reason the issue was assessed
as Moderate severity.

The FIPS modules in 3.6, 3.5 and 3.4 are not affected by this issue, as
PKCS#12 processing is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5 and 3.4 are vulnerable to this issue.

OpenSSL 3.3, 3.0, 1.1.1 and 1.0.2 are not affected by this issue as they do
not support PBMAC1 in PKCS#12.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-11187

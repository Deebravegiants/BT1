# [H] ALPINE-CVE-2026-34180

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34180
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34180
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.7-r0

## Details
Issue summary: Parsing a crafted DER-encoded ASN.1 structure with a primitive
element whose content exceeds 2 gigabytes in length may cause a heap buffer
over-read on 64-bit Unix and Unix-like platforms.

Impact summary: The heap buffer over-read may crash the application (Denial of
Service) or to load into the decoded ASN.1 object contents of memory beyond the
end of the input buffer.  More typically such ASN.1 elements would instead be
truncated.

An integer truncation in OpenSSL's ASN.1 decoder causes the content length of
an ASN.1 primitive element to be mishandled when it exceeds 2 gigabytes. In the
worst case the truncated length is treated as a request to scan the binary
content for a terminating zero byte, possibly causing OpenSSL to read either
less than or beyond the end of the allocated buffer.

Applications that pass attacker-supplied data to d2i_X509(), d2i_PKCS7(), or
any other d2i_* decoding function are affected. OpenSSL's own command-line
tools are not vulnerable, as data read through the BIO layer is checked before
it reaches the affected code. The issue only affects 64-bit Unix and Unix-like
platforms; 32-bit platforms and 64-bit Windows are not affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4 and 3.0 are not affected by this issue,
as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34180

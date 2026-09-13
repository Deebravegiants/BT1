# [H] Issue summary: Parsing a crafted DER-encoded ASN.1 structure with a primitive element whose...

## Summary
Severity: High
Advisory: JLSEC-2026-1133
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1133
Type: osv

## Affected
- Julia: `AppBundler` — affected >=1.0.0 <1.0.1
- Julia: `OpenSSL_jll` — affected >=0 <3.5.7+0
- Julia: `Openresty_jll` — affected unspecified

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

Applications that pass attacker-supplied data to `d2i_X509()`, `d2i_PKCS7()`, or
any other `d2i_`* decoding function are affected. OpenSSL's own command-line
tools are not vulnerable, as data read through the BIO layer is checked before
it reaches the affected code. The issue only affects 64-bit Unix and Unix-like
platforms; 32-bit platforms and 64-bit Windows are not affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4 and 3.0 are not affected by this issue,
as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://github.com/advisories/GHSA-3c8f-qq7h-7qv6
- https://github.com/openssl/openssl/commit/1c6908e4fa5fa568752221d8eaf561a809751e5d
- https://github.com/openssl/openssl/commit/cbe418ae978539cf14a398a207dba834c0e93e83
- https://github.com/openssl/openssl/commit/d93853c42110d6319e3df07842b488cb9f7ac5ff
- https://github.com/openssl/openssl/commit/da5d62af75f69d6fbf7803743d7c56ac75461e43
- https://github.com/openssl/openssl/commit/f696c73c3e61b8c502d040af62e690c060908a16
- https://github.com/openssl/security/commit/1c6908e4fa5fa568752221d8eaf561a809751e5d
- https://github.com/openssl/security/commit/cbe418ae978539cf14a398a207dba834c0e93e83
- https://github.com/openssl/security/commit/d93853c42110d6319e3df07842b488cb9f7ac5ff
- https://github.com/openssl/security/commit/da5d62af75f69d6fbf7803743d7c56ac75461e43
- https://github.com/openssl/security/commit/f696c73c3e61b8c502d040af62e690c060908a16
- https://nvd.nist.gov/vuln/detail/CVE-2026-34180
- https://openssl-library.org/news/secadv/20260609.txt

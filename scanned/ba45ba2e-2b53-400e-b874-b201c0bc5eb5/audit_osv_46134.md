# [H] An integer underflow issue exists in wolfSSL when parsing the Subject Alternative Name (SAN)...

## Summary
Severity: High
Advisory: JLSEC-2026-715
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-715
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
An integer underflow issue exists in wolfSSL when parsing the Subject Alternative Name (SAN) extension of X.509 certificates. A malformed certificate can specify an entry length larger than the enclosing sequence, causing the internal length counter to wrap during parsing. This results in incorrect handling of certificate data. The issue is limited to configurations using the original ASN.1 parsing implementation which is off by default.

## References
- https://github.com/advisories/GHSA-9qgc-pcpx-g38q
- https://github.com/wolfSSL/wolfssl/pull/10024
- https://nvd.nist.gov/vuln/detail/CVE-2026-5188

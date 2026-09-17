# [H] CVE-2026-43820

## Summary
Severity: High
Advisory: CVE-2026-43820
Aliases: GHSA-xfxg-9975-pc2j
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-43820
Type: osv

## Details
NIOSSLCertificate._subjectAlternativeNames provides access to the raw bytes for a cert's SANs. NIOSSL provides access to a buffer assumed to be backed by an ASN1_STRING, but not all SANs are backed by ASN1_STRING, so accessing the buffer for such a type can lead to out-of-bounds memory access. This vulnerability is addressed in swift-nio-ssl version 2.37.2.

## References
- https://github.com/apple/swift-nio-ssl/security/advisories/GHSA-xfxg-9975-pc2j

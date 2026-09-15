# [H] ALPINE-CVE-2025-32988

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-32988
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-32988
Type: osv

## Affected
- Alpine:v3.20: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.21: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.22: `gnutls` — affected >=0 <3.8.12-r0
- Alpine:v3.23: `gnutls` — affected >=0 <3.8.11-r0
- Alpine:v3.24: `gnutls` — affected >=0 <3.8.11-r0

## Details
A flaw was found in GnuTLS. A double-free vulnerability exists in GnuTLS due to incorrect ownership handling in the export logic of Subject Alternative Name (SAN) entries containing an otherName. If the type-id OID is invalid or malformed, GnuTLS will call asn1_delete_structure() on an ASN.1 node it does not own, leading to a double-free condition when the parent function or caller later attempts to free the same structure.

This vulnerability can be triggered using only public GnuTLS APIs and may result in denial of service or memory corruption, depending on allocator behavior.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-32988

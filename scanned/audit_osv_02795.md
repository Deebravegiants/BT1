# [M] ALPINE-CVE-2023-2650

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-2650
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2650
Type: osv

## Affected
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1u-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1u-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.9-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.1.1-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.9-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.9-r0

## Details
Issue summary: Processing some specially crafted ASN.1 object identifiers or
data containing them may be very slow.

Impact summary: Applications that use OBJ_obj2txt() directly, or use any of
the OpenSSL subsystems OCSP, PKCS7/SMIME, CMS, CMP/CRMF or TS with no message
size limit may experience notable to very long delays when processing those
messages, which may lead to a Denial of Service.

An OBJECT IDENTIFIER is composed of a series of numbers - sub-identifiers -
most of which have no size limit.  OBJ_obj2txt() may be used to translate
an ASN.1 OBJECT IDENTIFIER given in DER encoding form (using the OpenSSL
type ASN1_OBJECT) to its canonical numeric text form, which are the
sub-identifiers of the OBJECT IDENTIFIER in decimal form, separated by
periods.

When one of the sub-identifiers in the OBJECT IDENTIFIER is very large
(these are sizes that are seen as absurdly large, taking up tens or hundreds
of KiBs), the translation to a decimal number in text may take a very long
time.  The time complexity is O(n^2) with 'n' being the size of the
sub-identifiers in bytes (*).

With OpenSSL 3.0, support to fetch cryptographic algorithms using names /
identifiers in string form was introduced.  This includes using OBJECT
IDENTIFIERs in canonical numeric text form as identifiers for fetching
algorithms.

Such OBJECT IDENTIFIERs may be received through the ASN.1 structure
AlgorithmIdentifier, which is commonly used in multiple protocols to specify
what cryptographic algorithm should be used to sign or verify, encrypt or
decrypt, or digest passed data.

Applications that call OBJ_obj2txt() directly with untrusted data are
affected, with any version of OpenSSL.  If the use is for the mere purpose
of display, the severity is considered low.

In OpenSSL 3.0 and newer, this affects the subsystems OCSP, PKCS7/SMIME,
CMS, CMP/CRMF or TS.  It also impacts anything that processes X.509
certificates, including simple things like verifying its signature.

The impact on TLS is relatively low, because all versions of OpenSSL have a
100KiB limit on the peer's certificate chain.  Additionally, this only
impacts clients, or servers that have explicitly enabled client
authentication.

In OpenSSL 1.1.1 and 1.0.2, this only affects displaying diverse objects,
such as X.509 certificates.  This is assumed to not happen in such a way
that it would cause a Denial of Service, so these versions are considered
not affected by this issue in such a way that it would be cause for concern,
and the severity is therefore considered low.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2650

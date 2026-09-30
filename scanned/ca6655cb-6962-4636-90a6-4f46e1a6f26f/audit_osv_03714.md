# [M] ALPINE-CVE-2026-42769

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42769
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42769
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.4.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.4.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.4.0 <3.5.7-r0

## Details
Issue Summary: An error in the callback used to verify the certificate
provided in a Root CA key update Certificate Management Protocol (CMP)
message response rendered the certificate validation ineffectual, which
could lead to escalation of credentials from the Registration Authority (RA)
level to the root Certification Authority (root CA) level.

Impact Summary: The Registration Autority could replace the root CA
certificate for the CMP clients with an arbitrary root CA certificate.

One of the parts of the Certificate Management Protocol (CMP), specified in
RFC 9810, is Root Certification Authority (root CA) key Rollover,
which is sent by the server in a message with type 'id-it-rootCaKeyUpdate'.
As part of these messages, 'newWithOld' certificate, the new root CA
certificate signed with the old root CA key, is provided, and verifying its
signature is crucial for transferring the trust from the old CA key to the
new one.

The 'id-it-rootCaKeyUpdate' messages are expected to be processed with
OSSL_CMP_get1_rootCaKeyUpdate(), that is expected to verify the 'newWithOld'
certificate.  A typo in the certificate chain building code led to adding
an incorrect certificate ('newWithOld' instead of 'oldRoot') to the
certificate chain, rendering the certificate verification process ineffectual
(only the issuer name and the algorithm OIDs were verified by other parts
of the verification code).

An attacker who already has credentials that satisfy the CMP message
protection checks can generate a new key pair and use a crafted self-signed
certificate in its 'id-it-rootCaKeyUpdate' CMP messages which affected CMP
clients would accept as a new trust anchor.

Significant preconditions for the attack (having valid RA-level credentials)
are the reason the issue was assigned Low severity.

The FIPS modules are not affected by this issue, as the affected code is
outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42769

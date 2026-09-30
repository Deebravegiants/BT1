# [C] ALPINE-CVE-2026-34182

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-34182
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34182
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.5.7-r0

## Details
Issue Summary: Cryptographic Message Services (CMS) processing fails to perform
sufficient input validation on the cipher and tag length fields of
AuthEnvelopedData containers, leading to various potential compromises.

Impact Summary: Attackers making use of these vulnerabilities may achieve
key-equivalent functionality for a given CMS recipient and/or bypass integrity
validation for a given message.

In one use case, an attacker may send a CMS message containing
AuthEnvelopedData with the cipher specified as a non-AEAD cipher.  OpenSSL
erroneously allows this selection, and attempts to decrypt and validate the
message.

An on-path attacker who captures one legitimate AES-GCM AuthEnvelopedData
addressed to the victim can re-emit it with the recipientInfos set left
byte-for-byte intact, so the victim's private key still unwraps the genuine CEK
(the content-encryption key), but with the inner OID rewritten to AES-256-OFB
(Output Feedback Mode, an unauthenticated keystream mode) and with an
attacker-chosen IV and ciphertext. The victim initializes AES-256-OFB under the
real CEK, never consults the MAC field, and CMS_decrypt() returns success.

If the application under attack responds to the attacker with any indicator
showing success or failure of the decryption effort, it is possible for the
attacker to use this as an oracle to obtain key equivalent functionality for the
CEK used for the chosen recipient of the message.

In another use case, an attacker can reduce the tag length of the chosen AEAD
cipher for a given AuthEnvelopedData container to be a single byte long,
allowing an attacker to brute force CMS decryption, producing an integrity
bypass for applications that trust CMS_decrypt() to reject modified content.

The FIPS modules are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34182

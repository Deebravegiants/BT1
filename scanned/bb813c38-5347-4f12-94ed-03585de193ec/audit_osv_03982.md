# [H] ALPINE-CVE-2026-9076

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-9076
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9076
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.7-r0

## Details
Issue summary: When CMS password-based decryption (RFC 3211 / PWRI key unwrap)
processes attacker-supplied CMS data, an attacker-chosen stream-mode KEK
cipher can trigger a heap out-of-bounds read in kek_unwrap_key().

Impact summary: A heap buffer over-read may trigger a crash which leads to
Denial of Service for an application if the input buffer ends at a memory
page boundary and the following page is unmapped. There is no information
disclosure as the over-read bytes are not revealed to the attacker.

The key unwrapping function performs a check-byte test as specified in the
RFC that reads 7 bytes from a heap allocation that is based on the wrapped
key length from the message. There is a minimum length check based on the
block length of the wrapping cipher. However the cipher is selected from
an OID carried in the attacker's PWRI keyEncryptionAlgorithm with no
requirement that the cipher be a block cipher. When an attacker selects
a stream-mode cipher the guard will be ineffective and the allocated buffer
containing the unwrapped key can be too small to fit the check-bytes
specified in the RFC and a buffer over-read can happen.

Applications calling CMS_decrypt() or CMS_decrypt_set1_password()
(equivalently openssl cms -decrypt -pwri_password ...) on untrusted CMS
data are vulnerable to this issue. No password knowledge is required: the
over-read happens during the unwrap attempt before any authentication
succeeds.

The over-read is limited to a few bytes and is not written to output, so
there is no information disclosure. Triggering a crash requires the
allocation to border unmapped memory, which is unlikely with the normal
allocator.

The FIPS modules are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9076

# [H] ALPINE-CVE-2026-63072

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-63072
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-63072
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

## Details
Issue summary: OpenSSL CMS decryption sizes the key-unwrap output buffer based
on querying the unwrapped key size, but the AES-WRAP-PAD unwrap primitive
can write and cleanse more bytes than that query reports, causing an 8-byte
out-of-bounds heap write.

Impact summary: An attacker who supplies a crafted CMS message can trigger a
deterministic 8-byte out-of-bounds heap write when the victim decrypts it
with CMS_decrypt(), corrupting the heap and typically resulting in a Denial
of Service.

CWE: CWE-787: Out-of-bounds Write

Description: The key-wrap OID is potentially attacker-controlled on the wire.
CMS unwrapping allows both id-aesNNN-wrap-pad and id-aesNNN-wrap ciphers.
An attacker can take a legitimate message and change a single OID byte to
select the padded variant while leaving the message otherwise valid. Since
the unwrap key is derived from the recipient's private operation (ECDH key
agreement or ML-KEM decapsulation), the RFC 5649 integrity check cannot
pass, and the decryption fails with integrity failure.

The write is a fixed-size (8-byte), fixed-value (zero) heap overflow
immediately past the allocation, requires no special configuration, and is
reachable from the public CMS_decrypt() function. The consequence is
a heap corruption leading to a Denial of Service. The fix in the CMS code
sizes the unwrap output buffer for the worst case so a failed unwrap cannot
write past the allocation.

FIPS impact: no

As the CMS code lives outside the FIPS module boundary, no FIPS
modules are affected by this CVE.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-63072

# [H] CryptX versions before 0.088_001 for Perl have a stack buffer overflow in four AEAD decrypt_verify helpers

## Summary
Severity: High
Advisory: CVE-2026-41565
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-41565
Type: osv

## Details
CryptX versions before 0.088_001 for Perl have a stack buffer overflow in four AEAD decrypt_verify helpers.

The gcm_decrypt_verify, ccm_decrypt_verify, chacha20poly1305_decrypt_verify and eax_decrypt_verify XS routines copied the caller-supplied authentication tag into a fixed 144-byte stack buffer (MAXBLOCKSIZE) without checking the supplied length. A longer tag overwrites the stack past the buffer. Version 0.088 added the clamp to gcm_decrypt_verify, and 0.088_001 added it to the other three.

Any caller of an affected helper that forwards an attacker-controlled tag longer than the buffer can trigger the overflow.

## References
- http://www.openwall.com/lists/oss-security/2026/05/28/10
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41565.json
- https://metacpan.org/release/MIK/CryptX-0.088_001
- https://nvd.nist.gov/vuln/detail/CVE-2026-41565
- https://github.com/DCIT/perl-CryptX/commit/57e69e541b0718ca8724c2f61514322a2d859bc1.patch
- https://github.com/DCIT/perl-CryptX/commit/7e56347d420aaf43b2ee1586f4a230492ccf1642.patch
- https://github.com/DCIT/perl-CryptX

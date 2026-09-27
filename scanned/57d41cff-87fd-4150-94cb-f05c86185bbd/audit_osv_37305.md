# [C] Crypt::NaCl::Sodium versions through 2.002 for Perl has potential integer overflows

## Summary
Severity: Critical
Advisory: CVE-2026-30909
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-08
Source: https://osv.dev/vulnerability/CVE-2026-30909
Type: osv

## Details
Crypt::NaCl::Sodium versions through 2.002 for Perl has potential integer overflows.

bin2hex, encrypt, aes256gcm_encrypt_afternm and seal functions do not check that output size will be less than SIZE_MAX, which could lead to integer wraparound causing an undersized output buffer.

Encountering this issue is unlikely as the message length would need to be very large.

For bin2hex() the bin_len would have to be > SIZE_MAX / 2 For encrypt() the msg_len would need to be > SIZE_MAX - 16U For aes256gcm_encrypt_afternm() the msg_len would need to be > SIZE_MAX - 16U For seal() the enc_len would need to be > SIZE_MAX - 64U

## References
- http://www.openwall.com/lists/oss-security/2026/03/08/1
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Crypt-NaCl-Sodium-2.002/source/Sodium.xs#L2116
- https://metacpan.org/release/TIMLEGGE/Crypt-NaCl-Sodium-2.002/source/Sodium.xs#L2310
- https://metacpan.org/release/TIMLEGGE/Crypt-NaCl-Sodium-2.002/source/Sodium.xs#L3304
- https://metacpan.org/release/TIMLEGGE/Crypt-NaCl-Sodium-2.002/source/Sodium.xs#L942
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30909.json
- https://metacpan.org/release/TIMLEGGE/Crypt-NaCl-Sodium-2.003/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-30909
- https://github.com/cpan-authors/crypt-nacl-sodium/pull/24.patch
- https://github.com/cpan-authors/crypt-nacl-sodium

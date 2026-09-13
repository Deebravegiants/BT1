# [C] CVE-2018-25099

## Summary
Severity: Critical
Advisory: CVE-2018-25099
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2018-25099
Type: osv

## Details
In the CryptX module before 0.062 for Perl, gcm_decrypt_verify() and chacha20poly1305_decrypt_verify() do not verify the tag.

## References
- https://metacpan.org/dist/CryptX/changes
- https://github.com/DCIT/perl-CryptX/issues/47
- https://github.com/libtom/libtomcrypt/pull/451

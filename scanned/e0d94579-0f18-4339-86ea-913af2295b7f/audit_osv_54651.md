# [M] CVE-2024-2467

## Summary
Severity: Medium
Advisory: CVE-2024-2467
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-2467
Type: osv

## Details
A timing-based side-channel flaw exists in the perl-Crypt-OpenSSL-RSA package, which could be sufficient to recover plaintext across a network in a Bleichenbacher-style attack. To achieve successful decryption, an attacker would have to be able to send a large number of trial messages. The vulnerability affects the legacy PKCS#1v1.5 RSA encryption padding mode.

## References
- https://access.redhat.com/security/cve/CVE-2024-2467
- https://people.redhat.com/~hkario/marvin/
- https://bugzilla.redhat.com/show_bug.cgi?id=2269567
- https://github.com/toddr/Crypt-OpenSSL-RSA/issues/42

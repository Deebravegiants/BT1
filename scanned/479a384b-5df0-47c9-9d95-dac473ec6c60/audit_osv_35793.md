# [H] Crypt::DSA versions before 1.22 for Perl draw the DSA signing nonce and private key from a biased random generator, leading to private-key recovery

## Summary
Severity: High
Advisory: CVE-2026-14570
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-05
Source: https://osv.dev/vulnerability/CVE-2026-14570
Type: osv

## Details
Crypt::DSA versions before 1.22 for Perl draw the DSA signing nonce and private key from a biased random generator, leading to private-key recovery.

"Crypt::DSA::Util::makerandom forces the high bit of every value it returns to obtain an exactly N-bit integer for prime search. The signing nonce and the private key are drawn from makerandom. Because the high bit is always set, the result is not uniform: its top bit is fixed, producing insecure values."

An attacker who collects a modest number of signatures under an affected key, together with the public key, can recover the private key with a lattice attack.

Keys used to sign with an affected version should be considered compromised and new keys should be generated.

## References
- http://www.openwall.com/lists/oss-security/2026/07/05/1
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.21/source/lib/Crypt/DSA/Util.pm#L56
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.22/diff/TIMLEGGE/Crypt-DSA-1.21#lib/Crypt/DSA/Util.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14570.json
- https://metacpan.org/release/TIMLEGGE/Crypt-DSA-1.22/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-14570
- https://github.com/perl-Crypt-OpenPGP/Crypt-DSA

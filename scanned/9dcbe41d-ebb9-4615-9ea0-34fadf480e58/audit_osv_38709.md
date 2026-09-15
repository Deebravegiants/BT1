# [H] CryptX versions before 0.088 for Perl do not reseed the Crypt::PK PRNG state after forking

## Summary
Severity: High
Advisory: CVE-2026-41564
Aliases: GHSA-24c2-gp6c-24c6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41564
Type: osv

## Details
CryptX versions before 0.088 for Perl do not reseed the Crypt::PK PRNG state after forking.

The Crypt::PK::RSA, Crypt::PK::DSA, Crypt::PK::DH, Crypt::PK::ECC, Crypt::PK::Ed25519 and Crypt::PK::X25519 modules seed a per-object PRNG state in their constructors and reuse it without fork detection. A Crypt::PK::* object created before `fork()` shares byte-identical PRNG state with every child process, and any randomized operation they perform can produce identical output, including key generation. Two ECDSA or DSA signatures from different processes are enough to recover the signing private key through nonce-reuse key recovery.

This affects preforking services such as the Starman web server, where a Crypt::PK::* object loaded at startup is inherited by every worker process.

## References
- http://www.openwall.com/lists/oss-security/2026/04/23/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41564.json
- https://github.com/DCIT/perl-CryptX/security/advisories/GHSA-24c2-gp6c-24c6
- https://metacpan.org/release/MIK/CryptX-0.088
- https://nvd.nist.gov/vuln/detail/CVE-2026-41564
- https://github.com/DCIT/perl-CryptX/commit/9a1dd3e0c27d68e32450be5538b864c2b115ee15.patch
- https://github.com/DCIT/perl-CryptX

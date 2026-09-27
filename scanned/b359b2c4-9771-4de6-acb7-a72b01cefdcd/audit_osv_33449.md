# [M] Authen::SASL::Perl::DIGEST_MD5 versions 2.04 through 2.1800 for Perl generates the cnonce insecurely

## Summary
Severity: Medium
Advisory: CVE-2025-40918
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-40918
Type: osv

## Details
Authen::SASL::Perl::DIGEST_MD5 versions 2.04 through 2.1800 for Perl generates the cnonce insecurely.

The cnonce (client nonce) is generated from an MD5 hash of the PID, the epoch time and the built-in rand function. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

According to RFC 2831, The cnonce-value is an opaque quoted string value provided by the client and used by both client and server to avoid chosen plaintext attacks, and to provide mutual authentication. The security of the implementation
 depends on a good choice. It is RECOMMENDED that it contain at least 64 bits of entropy.

## References
- http://www.openwall.com/lists/oss-security/2025/07/16/5
- https://cpan.org/modules
- https://datatracker.ietf.org/doc/html/rfc2831
- https://metacpan.org/dist/Authen-SASL/source/lib/Authen/SASL/Perl/DIGEST_MD5.pm#L263
- https://metacpan.org/release/EHUELS/Authen-SASL-2.1900/changes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40918.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40918
- https://github.com/gbarr/perl-authen-sasl/pull/22
- https://security.metacpan.org/patches/A/Authen-SASL/2.1800/CVE-2025-40918-r1.patch
- https://github.com/gbarr/perl-authen-sasl

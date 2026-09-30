# [H] Catalyst::Authentication::Credential::HTTP versions 1.018 and earlier for Perl use insecurely generated nonces

## Summary
Severity: High
Advisory: CVE-2025-40920
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-40920
Type: osv

## Details
Catalyst::Authentication::Credential::HTTP versions 1.018 and earlier for Perl generate nonces using the Perl Data::UUID library.
  *  Data::UUID does not use a strong cryptographic source for generating UUIDs.
  *  Data::UUID returns v3 UUIDs, which are generated from known information and are unsuitable for security, as per RFC 9562.
  *  The nonces should be generated from a strong cryptographic source, as per RFC 7616.

## References
- http://www.openwall.com/lists/oss-security/2025/08/12/1
- https://cpan.org/modules
- https://datatracker.ietf.org/doc/html/rfc7616#section-5.12
- https://datatracker.ietf.org/doc/html/rfc9562#name-security-considerations
- https://metacpan.org/release/ETHER/Catalyst-Authentication-Credential-HTTP-1.018/source/lib/Catalyst/Authentication/Credential/HTTP.pm#L391
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40920.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40920
- https://github.com/perl-catalyst/Catalyst-Authentication-Credential-HTTP/pull/1
- https://github.com/perl-catalyst/Catalyst-Authentication-Credential-HTTP/commit/ad2c03aad95406db4ce35dfb670664ebde004c18
- https://security.metacpan.org/patches/C/Catalyst-Authentication-Credential-HTTP/1.018/CVE-2025-40920-r1.patch
- https://github.com/perl-catalyst/Catalyst-Authentication-Credential-HTTP

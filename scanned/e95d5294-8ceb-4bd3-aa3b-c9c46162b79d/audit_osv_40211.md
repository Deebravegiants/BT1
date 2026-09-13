# [H] Apache::API::Password versions through 0.5.2 for Perl can generate insecure random values for salts

## Summary
Severity: High
Advisory: CVE-2026-5088
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-5088
Type: osv

## Details
Apache::API::Password versions through 0.5.2 for Perl can generate insecure random values for salts.

The _make_salt and _make_salt_bcrypt methods will attept to load Crypt::URandom and then Bytes::Random::Secure to generate random bytes for the salt.  If those modules are unavailable, it will simply return 16 bytes generated with Perl's built-in rand function.

The rand function is unsuitable for cryptographic use.

These salts are used for password hashing.

## References
- http://www.openwall.com/lists/oss-security/2026/04/15/4
- http://www.openwall.com/lists/oss-security/2026/04/15/5
- https://cpan.org/modules
- https://metacpan.org/pod/Crypt::URandom
- https://metacpan.org/release/JDEGUEST/Apache2-API-v0.5.2/view/lib/Apache2/API/Password.pod
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5088.json
- https://metacpan.org/release/JDEGUEST/Apache2-API-v0.5.3/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-5088
- https://gitlab.com/jackdeguest/Apache2-API
- https://security.metacpan.org/docs/guides/random-data-for-security.html

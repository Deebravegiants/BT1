# [C] Net::SAML2 versions before 0.86 for Perl allow authentication bypass because _verify_encrypted_assertion accepts an EncryptedAssertion whose decrypted content carries no signature

## Summary
Severity: Critical
Advisory: CVE-2026-18108
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18108
Type: osv

## Details
Net::SAML2 versions before 0.86 for Perl allow authentication bypass because _verify_encrypted_assertion accepts an EncryptedAssertion whose decrypted content carries no signature.

_verify_encrypted_assertion decrypts the EncryptedAssertion and returns it as verified when it carries no signature, via "return $xml unless $xpath->exists('dsig:Signature', $assert);". The signature check and the trust anchor check that follow run only when a signature is present, so a decrypted assertion with no dsig:Signature element reaches new_from_xml unverified and its NameID and attributes are read into the assertion object. An SP's encryption certificate is published in its SAML metadata so the IdP can encrypt to it, so any party can encrypt an unsigned assertion to that certificate, wrap it in a samlp:Response, and post it to the assertion consumer service.

Any caller that configures a decryption key_file, and so accepts EncryptedAssertions, takes identity fields from an assertion that no trust anchor covers, and an unauthenticated party can authenticate as an arbitrary user. Callers with no key_file configured do not decrypt and are unaffected.

## References
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.85/source/lib/Net/SAML2/Protocol/Assertion.pm#L78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18108.json
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.86/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-18108
- https://github.com/perl-net-saml2/perl-Net-SAML2/commit/d916468586404518b8cf3c78dbd001cc1f1046a7.patch
- https://github.com/perl-net-saml2/perl-Net-SAML2

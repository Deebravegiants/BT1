# [H] Net::SAML2 versions before 0.86 for Perl allow SAML authentication bypass by verifying responses against the response-embedded certificate in verify_xml when no trust anchor is configured

## Summary
Severity: High
Advisory: CVE-2026-18089
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18089
Type: osv

## Details
Net::SAML2 versions before 0.86 for Perl allow SAML authentication bypass by verifying responses against the response-embedded certificate in verify_xml when no trust anchor is configured.

verify_xml in Net::SAML2::Role::VerifyXML runs "return if !$anchors && !$cacert;" as soon as the XML::Sig check succeeds, and that check uses the X.509 certificate taken from the response's own dsig:KeyInfo/dsig:X509Certificate element, so an unanchored response is checked only against the key it carries. Binding::POST declares cacert as an optional Maybe[Str] with no default, so a POST binding built without one takes that path, and _verify_encrypted_assertion returns early the same way with "return $xml unless $cacert;".

Any caller that constructs Binding::POST or calls Assertion->new_from_xml without a cacert, cert_text, or anchors argument accepts a response signed by an attacker generated key whose self-signed certificate is embedded in that response, authenticating an arbitrary assertion.

## References
- https://cpan.org/modules
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.85/source/lib/Net/SAML2/Binding/POST.pm#L21
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.85/source/lib/Net/SAML2/Protocol/Assertion.pm#L84
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.85/source/lib/Net/SAML2/Role/VerifyXML.pm#L32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18089.json
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.88/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-18089
- https://github.com/perl-net-saml2/perl-Net-SAML2

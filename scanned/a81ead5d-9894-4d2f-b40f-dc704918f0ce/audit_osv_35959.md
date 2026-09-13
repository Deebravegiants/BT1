# [H] Net::SAML2 versions before 0.86 for Perl allow SAML authentication bypass via XML signature wrapping because new_from_xml reads assertion identity with document-wide XPath instead of the signed subtree

## Summary
Severity: High
Advisory: CVE-2026-18092
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18092
Type: osv

## Details
Net::SAML2 versions before 0.86 for Perl allow SAML authentication bypass via XML signature wrapping because new_from_xml reads assertion identity with document-wide XPath instead of the signed subtree.

new_from_xml reads the NameID, attribute values, SessionIndex, audience and other identity fields with document-wide XPath, such as //saml:Assertion/saml:AttributeStatement/saml:Attribute and //saml:Subject/saml:NameID, which select the first matching element in document order rather than the element covered by the verified signature. handle_response confirms that a signature is present and, when a cacert is configured, that it chains to the CA, but XML::Sig verifies only the element named by the signature's Reference URI, so unsigned sibling assertions in the same document are not covered. An attacker who holds any one IdP-signed assertion can add an unsigned attacker-authored assertion earlier in document order; the signature still verifies and the document-order XPath returns the attacker's NameID and attributes.

Any caller that passes an untrusted Response to new_from_xml can accept identity fields from an assertion the IdP never signed, even when a cacert trust anchor is configured, so a party holding one valid IdP-signed assertion can authenticate as an arbitrary user.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18092.json
- https://metacpan.org/release/TIMLEGGE/Net-SAML2-0.86/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-18092
- https://github.com/perl-net-saml2/perl-Net-SAML2/commit/201fead7f42b83f40c84bf4a311a25b09acd18f9.patch
- https://github.com/perl-net-saml2/perl-Net-SAML2

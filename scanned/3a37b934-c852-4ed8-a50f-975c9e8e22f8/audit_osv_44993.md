# [C] XML::Sig versions before 0.71 for Perl allow signature wrapping via duplicate ID

## Summary
Severity: Critical
Advisory: CVE-2026-9487
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-9487
Type: osv

## Details
XML::Sig versions before 0.71 for Perl allow signature wrapping via duplicate ID.

_get_signed_xml() in lib/XML/Sig.pm, called from verify(), resolves the SignedInfo Reference/@URI to a node with the XPath expression "//*[@ID='$id']" and returns the first node of the resulting node set. A document in which two elements share that ID value is accepted: the digest and signature are checked against whichever element comes first in document order, and the duplicate is not detected.

Such a document verifies successfully while an application that resolves the same ID independently can read the second, attacker supplied element; in a SAML2 context this places the contents of an Assertion under attacker control.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9487.json
- https://metacpan.org/release/TIMLEGGE/XML-Sig-0.71/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9487
- https://github.com/perl-net-saml2/perl-XML-Sig/commit/4976bde5245df69b8e02c6ae061acbd4891cd7f9.patch
- https://github.com/perl-net-saml2/perl-XML-Sig

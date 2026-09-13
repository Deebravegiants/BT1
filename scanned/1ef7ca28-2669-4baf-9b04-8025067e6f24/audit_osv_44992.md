# [C] XML::Sig versions before 0.71 for Perl allow XPath injection in ID lookup

## Summary
Severity: Critical
Advisory: CVE-2026-9390
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-9390
Type: osv

## Details
XML::Sig versions before 0.71 for Perl allow XPath injection in ID lookup.

verify() and _get_signed_xml() in lib/XML/Sig.pm build XPath expressions by concatenating the SignedInfo/Reference/@URI value read from the document being verified. The value is neither escaped nor checked against the NCName grammar that XML requires of an ID, so a URI containing a single quote closes the string literal in the generated expression and appends arbitrary XPath operators.

A crafted URI can make the lookup match elements the reference does not name, or every element in the document, so which node is selected for digest verification is decided by the injected expression rather than by the reference.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9390.json
- https://metacpan.org/release/TIMLEGGE/XML-Sig-0.71/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9390
- https://github.com/perl-net-saml2/perl-XML-Sig/commit/69ad2b421118fadd33d57f50b110b8d161e8fef5.patch
- https://github.com/perl-net-saml2/perl-XML-Sig/commit/a85aad21aa767ac1c158bbfc19447683941ab376.patch
- https://github.com/perl-net-saml2/perl-XML-Sig

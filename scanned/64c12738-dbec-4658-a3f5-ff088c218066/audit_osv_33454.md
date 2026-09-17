# [C] XML-Sig prior to 0.68 for Perl improperly validates XML without signatures

## Summary
Severity: Critical
Advisory: CVE-2025-40934
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-40934
Type: osv

## Details
XML-Sig versions 0.27 through 0.67 for Perl incorrectly validates XML files if signatures are omitted.

An attacker can remove the signature from the XML document to make it pass the verification check.

XML-Sig is a Perl module to validate signatures on XML files.  An unsigned XML file should return an error message.  The affected versions return true when attempting to validate an XML file that contains no signatures.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40934.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40934
- https://github.com/perl-net-saml2/perl-XML-Sig/issues/63
- https://github.com/perl-net-saml2/perl-XML-Sig/pull/64
- https://github.com/perl-net-saml2/perl-XML-Sig

# [H] XML::Sig versions from 0.29 before 0.72 for Perl allow signature verification bypass because verify returns true when every signature was skipped before any cryptographic check

## Summary
Severity: High
Advisory: CVE-2026-18568
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-18568
Type: osv

## Details
XML::Sig versions from 0.29 before 0.72 for Perl allow signature verification bypass because verify returns true when every signature was skipped before any cryptographic check.

verify in lib/XML/Sig.pm counts the `//dsig:Signature` elements into `$numsigs` and iterates over them, but two paths reach `next` before any digest or key check runs: a `SignedInfo/Reference/@URI` that resolves to no element while `$numsigs` is greater than 1, and, when `id_attr` is set, a reference that does not match the requested ID. The loop records nothing about what it checked, so when every signature takes one of those paths control reaches the unconditional `return 1` that ends verify. Two `Signature` elements whose Reference URI names an ID that no element carries is enough, as is one such element combined with `id_attr`.

Any caller that passes untrusted XML to verify can receive a true return for a document in which no digest and no signature value was checked; a `cert` or `cert_text` trust anchor does not change this, because no key check runs. Versions up to 0.28 use an XML::XPath based verify that has no such skip and are not affected.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2025-40934
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18568.json
- https://metacpan.org/release/TIMLEGGE/XML-Sig-0.72/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-18568
- https://github.com/perl-net-saml2/perl-XML-Sig/commit/ef22cfed1ac0f29b316d17eb79cf6480e03ae16a.patch
- https://github.com/perl-net-saml2/perl-XML-Sig

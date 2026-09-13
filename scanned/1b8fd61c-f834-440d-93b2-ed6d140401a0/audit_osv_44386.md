# [H] XML::LibXML versions through 2.0210 for Perl read out-of-bounds heap memory when parsing XML node names containing truncated UTF-8 byte sequences

## Summary
Severity: High
Advisory: CVE-2026-8177
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/CVE-2026-8177
Type: osv

## Details
XML::LibXML versions through 2.0210 for Perl read out-of-bounds heap memory when parsing XML node names containing truncated UTF-8 byte sequences.

A node name ending in the middle of a multi byte UTF-8 sequence causes the parser to read past the end of the input string into adjacent heap memory.

Any Perl process that passes attacker controlled strings to XML::LibXML's DOM node-name methods can reach this path on the default API. The likely consequence is a crash, causing denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/05/10/8
- http://www.openwall.com/lists/oss-security/2026/05/11/2
- https://cpan.org/modules
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-8177.json
- https://access.redhat.com/errata/RHSA-2026:39547
- https://access.redhat.com/errata/RHSA-2026:39553
- https://access.redhat.com/errata/RHSA-2026:39878
- https://access.redhat.com/security/cve/CVE-2026-8177
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8177.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8177
- https://bugzilla.redhat.com/show_bug.cgi?id=2468684
- https://github.com/cpan-authors/XML-LibXML/issues/146
- https://github.com/cpan-authors/XML-LibXML/pull/149
- https://github.com/cpan-authors/XML-LibXML/commit/15652bd905a6c9dda59a81b14d4766adbbae2ea8.patch
- https://github.com/cpan-authors/XML-LibXML

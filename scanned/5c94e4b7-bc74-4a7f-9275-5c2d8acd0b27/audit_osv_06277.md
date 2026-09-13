# [H] DoS attack via DOMNode::C14N()

## Summary
Severity: High
Advisory: BIT-libphp-2026-7263
Aliases: BIT-php-2026-7263, BIT-php-min-2026-7263, CVE-2026-7263
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7263
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.4.* before 8.4.21 and 8.5.* before 8.5.6, DOMNode::C14N() method may process the XML data incorrectly, causing a circular linked list in the data structure representing the XML document. This may cause subsequent processing of the XML document to enter infinite loop, causing denial of service in the processing application.

## References
- https://github.com/php/php-src/security/advisories/GHSA-4jhr-8w89-j733
- https://nvd.nist.gov/vuln/detail/CVE-2026-7263
- https://access.redhat.com/errata/RHSA-2026:22649
- https://access.redhat.com/security/cve/CVE-2026-7263
- https://bugzilla.redhat.com/show_bug.cgi?id=2468572
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-7263.json

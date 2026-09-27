# [H] BIT-java-2025-24855

## Summary
Severity: High
Advisory: BIT-java-2025-24855
Aliases: BIT-java-min-2025-24855, BIT-jre-2025-24855, CVE-2025-24855
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2025-24855
Type: osv

## Affected
- Bitnami: `java` — affected >=1.9.0 <8.0.461

## Details
numbers.c in libxslt before 1.1.43 has a use-after-free because, in nested XPath evaluations, an XPath context node can be modified but never restored. This is related to xsltNumberFormatGetValue, xsltEvalXPathPredicate, xsltEvalXPathStringNs, and xsltComputeSortResultInternal.

## References
- https://gitlab.gnome.org/GNOME/libxslt/-/issues/128
- https://lists.debian.org/debian-lts-announce/2025/03/msg00015.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-24855

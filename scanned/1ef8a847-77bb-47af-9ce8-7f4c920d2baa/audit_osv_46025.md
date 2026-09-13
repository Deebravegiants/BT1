# [H] numbers.c in libxslt before 1.1.43 has a use-after-free because, in nested XPath evaluations, an...

## Summary
Severity: High
Advisory: JLSEC-2026-583
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-583
Type: osv

## Affected
- Julia: `XSLT_jll` — affected >=0 <1.1.43+0

## Details
numbers.c in libxslt before 1.1.43 has a use-after-free because, in nested XPath evaluations, an XPath context node can be modified but never restored. This is related to xsltNumberFormatGetValue, xsltEvalXPathPredicate, xsltEvalXPathStringNs, and xsltComputeSortResultInternal.

## References
- https://github.com/advisories/GHSA-3cgj-v3m4-cgcq
- https://gitlab.gnome.org/GNOME/libxslt/-/issues/128
- https://lists.debian.org/debian-lts-announce/2025/03/msg00015.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-24855

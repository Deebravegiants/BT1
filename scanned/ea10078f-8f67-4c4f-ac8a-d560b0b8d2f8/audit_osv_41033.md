# [H] YAML::Syck versions before 1.47 for Perl allow an out-of-bounds read via an unbounded newline scan in newline_len

## Summary
Severity: High
Advisory: CVE-2026-57077
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-57077
Type: osv

## Details
YAML::Syck versions before 1.47 for Perl allow an out-of-bounds read via an unbounded newline scan in newline_len.

In the bundled libsyck newline_len and is_newline dereference the scan pointer, and the following byte for a "\r\n" pair, with no NUL-terminator or bounds check. During block-scalar lexing at a document boundary the scan runs one byte past the heap lexer buffer. This is an incomplete fix of CVE-2025-11683, on a lexer path the earlier fix did not cover.

Any caller that runs Load or LoadFile on an untrusted document with a block scalar at a document boundary reaches the over-read.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2025-11683
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57077.json
- https://metacpan.org/release/TODDR/YAML-Syck-1.47/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-57077
- https://github.com/toddr/YAML-Syck/commit/44c90a109ec3215ee7ce747bd11209835e123d8b.patch
- https://github.com/toddr/YAML-Syck

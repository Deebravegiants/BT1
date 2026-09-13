# [H] HTML::Entities versions before 3.84 for Perl read freed heap memory in _decode_entities

## Summary
Severity: High
Advisory: CVE-2026-8829
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-8829
Type: osv

## Details
HTML::Entities versions before 3.84 for Perl read freed heap memory in _decode_entities.

The XS routine backing HTML::Entities::_decode_entities cached a pointer (repl) into the entity-value SV returned by hv_fetch on the entity2char hash. When the input SV was identical to a value SV in that hash, and that value contained its own key as an entity reference, a later call to grow_gap() reallocated the SV's PV buffer and freed the backing allocation that repl still pointed into. The subsequent copy loop read repl_len bytes from the freed allocation.

The read may disclose adjacent heap contents into the destination SV.

## References
- http://www.openwall.com/lists/oss-security/2026/06/04/2
- https://cpan.org/modules
- https://lists.debian.org/debian-lts-announce/2026/06/msg00044.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8829.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8829
- https://github.com/libwww-perl/HTML-Parser/commit/6922552b0778c90a9587a3894e248be4d3a25e1c.patch
- https://github.com/libwww-perl/HTML-Parser/pull/56
- https://github.com/libwww-perl/HTML-Parser

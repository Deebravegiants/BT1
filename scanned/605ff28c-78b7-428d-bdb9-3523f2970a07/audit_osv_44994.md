# [H] Cpanel::JSON::XS versions before 4.41 for Perl allow denial of service via UTF-8 BOM prefixed input when a decode filter callback throws

## Summary
Severity: High
Advisory: CVE-2026-9516
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-9516
Type: osv

## Details
Cpanel::JSON::XS versions before 4.41 for Perl allow denial of service via UTF-8 BOM prefixed input when a decode filter callback throws.

To skip a leading 3-byte UTF-8 BOM, decode_json() advances the input scalar's string pointer past the mark with SvPV_set() and restores it only on the normal return path. When decoding aborts through a Perl exception, for example a filter_json_object callback that croaks, the restore is skipped and the scalar is left with its string pointer offset into its own buffer and a shortened length.

When that scalar is later freed, the allocator receives an invalid pointer and the interpreter aborts. A single BOM prefixed document decoded with a throwing filter callback crashes any caller.

## References
- http://www.openwall.com/lists/oss-security/2026/06/03/5
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9516.json
- https://metacpan.org/release/RURBAN/Cpanel-JSON-XS-4.41/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9516
- https://github.com/rurban/Cpanel-JSON-XS/commit/dfe1b41a36caba51dc12a2917fe50285d1ffaa7b.patch
- https://github.com/rurban/Cpanel-JSON-XS

# [H] Cpanel::JSON::XS versions before 4.41 for Perl allow type confusion via duplicate object keys when dupkeys_as_arrayref is enabled

## Summary
Severity: High
Advisory: CVE-2026-9334
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-9334
Type: osv

## Details
Cpanel::JSON::XS versions before 4.41 for Perl allow type confusion via duplicate object keys when dupkeys_as_arrayref is enabled.

decode_hv() collapses duplicate object keys into an array reference under dupkeys_as_arrayref. The branch reached for a duplicate key tests `SvTYPE (old_value) != SVt_RV && SvTYPE (SvRV (old_value)) != SVt_PVAV`, which evaluates SvRV(old_value) before establishing that old_value is a reference. When the existing value is a plain scalar rather than an array reference, a non-reference scalar is dereferenced as a reference.

A caller decoding untrusted JSON with dupkeys_as_arrayref enabled is crashed, and the incompatible access follows a pointer taken from attacker controlled scalar contents.

## References
- http://www.openwall.com/lists/oss-security/2026/06/03/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9334.json
- https://metacpan.org/release/RURBAN/Cpanel-JSON-XS-4.41/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9334
- https://github.com/rurban/Cpanel-JSON-XS/commit/11a7c550a0d8fac2f84414f24d5df9b2bfe346e2.patch
- https://github.com/rurban/Cpanel-JSON-XS

# [H] A flaw was found in GLib. An off-by-one error can occur in the gvs_tuple_is_normal function in...

## Summary
Severity: High
Advisory: JLSEC-2026-1243
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1243
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.88.3+0

## Details
A flaw was found in GLib. An off-by-one error can occur in the `gvs_tuple_is_normal` function in the `glib/gvariant-serialiser.c` file when doing an alignment padding check because the bounds check uses > instead of >=, causing an out-of-bounds read of only 1 byte. This issue can cause a minor information disclosure of 1 byte and a denial of service when the out-of-bounds read crosses a page boundary.

## References
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/security/cve/CVE-2026-58010
- https://bugzilla.redhat.com/show_bug.cgi?id=2492243
- https://github.com/advisories/GHSA-m7rp-473c-296x
- https://gitlab.gnome.org/GNOME/glib/-/issues/3915
- https://nvd.nist.gov/vuln/detail/CVE-2026-58010

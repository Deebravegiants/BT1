# [C] A flaw was found in GLib. A state confusion issue exists in g_dbus_node_info_new_for_xml() in the...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1249
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1249
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.88.3+0

## Details
A flaw was found in GLib. A state confusion issue exists in `g_dbus_node_info_new_for_xml()` in the `gio/gdbusintrospection.c` file when processing malformed D-Bus introspection XML, specifically with a `node` element nested within other elements like `method`, `signal`, `property` or `arg`. This issue can cause an unsigned integer overflow and lead to an out-of-bounds read, resulting in a denial of service.

## References
- https://access.redhat.com/errata/RHSA-2026:42063
- https://access.redhat.com/errata/RHSA-2026:42089
- https://access.redhat.com/errata/RHSA-2026:42090
- https://access.redhat.com/errata/RHSA-2026:44481
- https://access.redhat.com/errata/RHSA-2026:46836
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/errata/RHSA-2026:51175
- https://access.redhat.com/errata/RHSA-2026:51176
- https://access.redhat.com/errata/RHSA-2026:51177
- https://access.redhat.com/errata/RHSA-2026:51181
- https://access.redhat.com/errata/RHSA-2026:51182
- https://access.redhat.com/errata/RHSA-2026:51183
- https://access.redhat.com/errata/RHSA-2026:51184
- https://access.redhat.com/errata/RHSA-2026:51185
- https://access.redhat.com/security/cve/CVE-2026-58016
- https://bugzilla.redhat.com/show_bug.cgi?id=2492257
- https://github.com/advisories/GHSA-8rpw-4xx7-27w7
- https://gitlab.gnome.org/GNOME/glib/-/issues/3932
- https://nvd.nist.gov/vuln/detail/CVE-2026-58016

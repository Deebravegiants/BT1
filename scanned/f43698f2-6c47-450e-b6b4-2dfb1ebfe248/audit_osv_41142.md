# [H] Glib: integer underflow in gio/gdbusintrospection.c via "g_dbus_node_info_new_for_xml"

## Summary
Severity: High
Advisory: CVE-2026-58016
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58016
Type: osv

## Details
A flaw was found in GLib. A state confusion issue exists in g_dbus_node_info_new_for_xml() in the gio/gdbusintrospection.c file when processing malformed D-Bus introspection XML, specifically with a `node` element nested within other elements like `method`, `signal`, `property` or `arg`. This issue can cause an unsigned integer overflow and lead to an out-of-bounds read, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
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
- https://access.redhat.com/errata/RHSA-2026:53371
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/security/cve/CVE-2026-58016
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58016.json

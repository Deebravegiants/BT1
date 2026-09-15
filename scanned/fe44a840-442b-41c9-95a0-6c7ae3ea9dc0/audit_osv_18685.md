# [H] CVE-2020-35457

## Summary
Severity: High
Advisory: CVE-2020-35457
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/CVE-2020-35457
Type: osv

## Details
GNOME GLib before 2.65.3 has an integer overflow, that might lead to an out-of-bounds write, in g_option_group_add_entries. NOTE: the vendor's position is "Realistically this is not a security issue. The standard pattern is for callers to provide a static list of option entries in a fixed number of calls to g_option_group_add_entries()." The researcher states that this pattern is undocumented

## References
- https://gitlab.gnome.org/GNOME/glib/-/releases/2.65.3
- https://gitlab.gnome.org/GNOME/glib/-/commit/63c5b62f0a984fac9a9700b12f54fe878e016a5d
- https://gitlab.gnome.org/GNOME/glib/-/issues/2197

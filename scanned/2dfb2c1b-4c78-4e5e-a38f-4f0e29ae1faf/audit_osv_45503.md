# [H] A flaw was found in GLib. An out-of-bounds read of only 2 bytes can occur in the...

## Summary
Severity: High
Advisory: JLSEC-2026-1244
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1244
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.88.3+0

## Details
A flaw was found in GLib. An out-of-bounds read of only 2 bytes can occur in the `g_date_time_get_ymd` function in the `glib/gdatetime.c` file when an invalid GDateTime object produced by the `g_date_time_add_full` function is processed. This flaw can corrupt the date output and potentially cause logic errors that may lead to a denial of service.

## References
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/security/cve/CVE-2026-58011
- https://bugzilla.redhat.com/show_bug.cgi?id=2492245
- https://github.com/advisories/GHSA-8xmh-8wfg-9f6j
- https://gitlab.gnome.org/GNOME/glib/-/issues/3917
- https://gitlab.gnome.org/GNOME/glib/-/work_items/3917
- https://nvd.nist.gov/vuln/detail/CVE-2026-58011

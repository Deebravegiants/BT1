# [H] A flaw was found in GLib. A buffer over-read can occur in the g_regex_replace function when used...

## Summary
Severity: High
Advisory: JLSEC-2026-1245
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1245
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.88.3+0

## Details
A flaw was found in GLib. A buffer over-read can occur in the `g_regex_replace` function when used with the `G_REGEX_RAW` compile flag and case-change replacement escapes because the `string_append` function processes matched substrings using UTF-8 functions that assume valid UTF-8 input, even when the string is treated as raw bytes. This vulnerability can cause a minor information disclosure of 1-5 bytes and a denial of service when the buffer over-read crosses a page boundary.

## References
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/security/cve/CVE-2026-58012
- https://bugzilla.redhat.com/show_bug.cgi?id=2492247
- https://github.com/advisories/GHSA-vwg8-37h9-g38g
- https://gitlab.gnome.org/GNOME/glib/-/issues/3918
- https://nvd.nist.gov/vuln/detail/CVE-2026-58012

# [H] A flaw was found in GLib. The D-Bus client-side implementation of the DBUS_COOKIE_SHA1 SASL...

## Summary
Severity: High
Advisory: JLSEC-2026-1248
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/JLSEC-2026-1248
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.88.3+0

## Details
A flaw was found in GLib. The D-Bus client-side implementation of the `DBUS_COOKIE_SHA1` SASL authentication mechanism does not validate the `cookie_context` parameter received from the server. A malicious D-Bus server can supply a `cookie_context` containing path traversal sequences, causing the client to read an arbitrary file and exfiltrate sensitive data by verifying guessed file contents against a generated hash.

## References
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/security/cve/CVE-2026-58015
- https://bugzilla.redhat.com/show_bug.cgi?id=2492256
- https://github.com/advisories/GHSA-hmpf-72wc-2r6x
- https://gitlab.gnome.org/GNOME/glib/-/issues/3931
- https://nvd.nist.gov/vuln/detail/CVE-2026-58015

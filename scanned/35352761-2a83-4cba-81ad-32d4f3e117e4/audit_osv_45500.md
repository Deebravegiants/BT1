# [H] JLSEC-2026-1241

## Summary
Severity: High
Advisory: JLSEC-2026-1241
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/JLSEC-2026-1241
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.13.1+0 <2.15.3+0

## Details
A flaw was found in libxml2. This vulnerability occurs when the library processes a specially crafted XML Schema Definition (XSD) validated document that includes an internal entity reference. An attacker could exploit this by providing a malicious document, leading to a type confusion error that causes the application to crash. This results in a denial of service (DoS), making the affected system or application unavailable.

## References
- https://access.redhat.com/errata/RHSA-2026:11503
- https://access.redhat.com/security/cve/CVE-2026-6732
- https://bugzilla.redhat.com/show_bug.cgi?id=2461300
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/1097
- https://gitlab.gnome.org/GNOME/libxml2/-/merge_requests/411

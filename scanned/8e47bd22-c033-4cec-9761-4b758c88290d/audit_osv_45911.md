# [C] JLSEC-2026-468

## Summary
Severity: Critical
Advisory: JLSEC-2026-468
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-468
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.11.5+0 <2.13.3+0

## Details
In libxml2 2.11 before 2.11.9, 2.12 before 2.12.9, and 2.13 before 2.13.3, the SAX parser can produce events for external entities even if custom SAX handlers try to override entity content (by setting "checked"). This makes classic XXE attacks possible.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/1a8932303969907f6572b1b6aac4081c56adb5c6
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/761
- https://security.netapp.com/advisory/ntap-20250228-0004/

# [M] CVE-2020-36774

## Summary
Severity: Medium
Advisory: CVE-2020-36774
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2020-36774
Type: osv

## Details
plugins/gtk+/glade-gtk-box.c in GNOME Glade before 3.38.1 and 3.39.x before 3.40.0 mishandles widget rebuilding for GladeGtkBox, leading to a denial of service (application crash).

## References
- https://gitlab.gnome.org/GNOME/glade/-/issues/479
- https://gitlab.gnome.org/GNOME/glade/-/commit/7acdd3c6f6934f47b8974ebc2190a59ea5d2ed17

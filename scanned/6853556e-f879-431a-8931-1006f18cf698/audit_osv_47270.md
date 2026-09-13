# [H] CVE-2016-20011

## Summary
Severity: High
Advisory: CVE-2016-20011
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-05-25
Source: https://osv.dev/vulnerability/CVE-2016-20011
Type: osv

## Details
libgrss through 0.7.0 fails to perform TLS certificate verification when downloading feeds, allowing remote attackers to manipulate the contents of feeds without detection. This occurs because of the default behavior of SoupSessionSync.

## References
- https://bugzilla.gnome.org/show_bug.cgi?id=772647
- https://gitlab.gnome.org/GNOME/libgrss/-/issues/4
- https://gitlab.gnome.org/GNOME/libgrss/-/merge_requests/7.patch

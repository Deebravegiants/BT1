# [H] CVE-2021-28117

## Summary
Severity: High
Advisory: CVE-2021-28117
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-03-20
Source: https://osv.dev/vulnerability/CVE-2021-28117
Type: osv

## Details
libdiscover/backends/KNSBackend/KNSResource.cpp in KDE Discover before 5.21.3 automatically creates links to potentially dangerous URLs (that are neither https:// nor http://) based on the content of the store.kde.org web site. (5.18.7 is also a fixed version.)

## References
- https://github.com/KDE/discover/releases
- https://userbase.kde.org/Discover
- https://github.com/KDE/discover/commit/fcd3b30552bf03a384b1a16f9bb8db029c111356
- https://invent.kde.org/plasma/discover/commit/94478827aab63d2e2321f0ca9ec5553718798e60
- https://kde.org/info/security/advisory-20210310-1.txt

# [M] CVE-2025-66270

## Summary
Severity: Medium
Advisory: CVE-2025-66270
CVSS: 4.7 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66270
Type: osv

## Details
The KDE Connect protocol 8 before 2025-11-28 does not correlate device IDs across two packets. This affects KDE Connect before 25.12 on desktop, KDE Connect before 0.5.4 on iOS, KDE Connect before 1.34.4 on Android, GSConnect before 68, and Valent before 1.0.0.alpha.49.

## References
- https://invent.kde.org/network/kdeconnect-android/-/commit/675d2d24a1eb95d15d9e5bde2b7e2271d5ada6a9
- https://invent.kde.org/network/kdeconnect-ios/-/commit/6c003c22d04270cabc4b262d399c753d55cf9080
- https://invent.kde.org/network/kdeconnect-kde/-/commit/4e53bcdd5d4c28bd9fefd114b807ce35d7b3373e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66270.json
- https://kde.org/info/security/advisory-20251128-1.txt
- https://nvd.nist.gov/vuln/detail/CVE-2025-66270
- https://github.com/GSConnect/gnome-shell-extension-gsconnect/commit/a38246deec0af50ae218cdc51db32cdd7eb145e3
- https://github.com/andyholmes/valent/commit/85f773124a67ed1add79e7465bb088ec667cccce

# [M] Evolution-data-server: evolution data server: arbitrary file deletion via inconsistent uri handling

## Summary
Severity: Medium
Advisory: CVE-2026-2604
CVSS: 5.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-2604
Type: osv

## Details
A flaw was found in evolution-data-server. Inconsistent comparison logic in the addressbook file backend allows a Flatpak application with D-Bus access to craft a malicious URI containing directory traversal sequences. This URI is stored without proper validation during contact creation or modification. Later, during contact deletion, the URI is processed with a less strict check, leading to the deletion of arbitrary files on the host filesystem. This could potentially include critical Flatpak override files.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2026/03/msg00007.html
- https://access.redhat.com/security/cve/CVE-2026-2604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2604.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2604
- https://bugzilla.redhat.com/show_bug.cgi?id=2440301
- https://gitlab.gnome.org/GNOME/evolution-data-server/-/issues/627
- https://gitlab.gnome.org/GNOME/evolution-data-server/-/work_items/627

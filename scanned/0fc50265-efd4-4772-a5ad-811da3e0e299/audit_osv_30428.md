# [H] CVE-2024-52532

## Summary
Severity: High
Advisory: CVE-2024-52532
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-11
Source: https://osv.dev/vulnerability/CVE-2024-52532
Type: osv

## Details
GNOME libsoup before 3.6.1 has an infinite loop, and memory consumption. during the reading of certain patterns of WebSocket data from clients.

## References
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/12/msg00014.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52532.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52532
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/391
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/410

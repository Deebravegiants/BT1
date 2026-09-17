# [H] Networkmanager: networkmanager: 802-1x ca-path and phase2-ca-path bypass private_user restriction, allowing wpa-enterprise server validation bypass (incomplete fix for cve-2025-9615)

## Summary
Severity: High
Advisory: CVE-2026-19685
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-19685
Type: osv

## Details
NetworkManager did not apply the private_user restriction to the 802-1x.ca-path and phase2-ca-path directory-valued connection properties. This incomplete fix for CVE-2025-9615 allows an unprivileged local user to point a private WPA-Enterprise (802.1X) connection profile's CA path at an attacker-controlled directory, bypassing server certificate validation and enabling credential theft via a rogue access point.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-19685
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19685.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19685
- https://bugzilla.redhat.com/show_bug.cgi?id=2515042
- https://gitlab.freedesktop.org/NetworkManager/NetworkManager/-/commit/a8e87381a3e70060abd721d9a347f42b2ba68e6e
- https://gitlab.freedesktop.org/NetworkManager/NetworkManager/-/commit/e85cc46d0b36cdba50fe8411cc93d55a49ebfccf
- https://gitlab.freedesktop.org/NetworkManager/NetworkManager/-/merge_requests/2513

# [H] CVE-2021-33516

## Summary
Severity: High
Advisory: CVE-2021-33516
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2021-05-24
Source: https://osv.dev/vulnerability/CVE-2021-33516
Type: osv

## Details
An issue was discovered in GUPnP before 1.0.7 and 1.1.x and 1.2.x before 1.2.5. It allows DNS rebinding. A remote web server can exploit this vulnerability to trick a victim's browser into triggering actions against local UPnP services implemented using this library. Depending on the affected service, this could be used for data exfiltration, data tempering, etc.

## References
- https://gitlab.gnome.org/GNOME/gupnp/-/issues/24
- https://discourse.gnome.org/t/security-relevant-releases-for-gupnp-issue-cve-2021-33516/6536

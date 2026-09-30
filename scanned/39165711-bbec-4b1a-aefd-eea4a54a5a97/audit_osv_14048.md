# [H] CVE-2018-6560

## Summary
Severity: High
Advisory: CVE-2018-6560
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6560
Type: osv

## Details
In dbus-proxy/flatpak-proxy.c in Flatpak before 0.8.9, and 0.9.x and 0.10.x before 0.10.3, crafted D-Bus messages to the host can be used to break out of the sandbox, because whitespace handling in the proxy is not identical to whitespace handling in the daemon.

## References
- https://access.redhat.com/errata/RHSA-2018:2766
- https://github.com/flatpak/flatpak/releases/tag/0.10.3
- https://github.com/flatpak/flatpak/releases/tag/0.8.9
- https://github.com/flatpak/flatpak/commit/52346bf187b5a7f1c0fe9075b328b7ad6abe78f6

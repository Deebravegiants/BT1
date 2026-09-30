# [C] TIOCLINUX can send commands outside sandbox if running on a virtual console

## Summary
Severity: Critical
Advisory: CVE-2023-28100
Aliases: GHSA-7qpw-3vjv-xrqp
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-03-16
Source: https://osv.dev/vulnerability/CVE-2023-28100
Type: osv

## Details
Flatpak is a system for building, distributing, and running sandboxed desktop applications on Linux. Versions prior to 1.10.8, 1.12.8, 1.14.4, and 1.15.4 contain a vulnerability similar to CVE-2017-5226, but using the `TIOCLINUX` ioctl command instead of `TIOCSTI`. If a Flatpak app is run on a Linux virtual console such as `/dev/tty1`, it can copy text from the virtual console and paste it into the command buffer, from which the command might be run after the Flatpak app has exited. Ordinary graphical terminal emulators like xterm, gnome-terminal and Konsole are unaffected. This vulnerability is specific to the Linux virtual consoles `/dev/tty1`, `/dev/tty2` and so on. A patch is available in versions 1.10.8, 1.12.8, 1.14.4, and 1.15.4. As a workaround, don't run Flatpak on a Linux virtual console. Flatpak is primarily designed to be used in a Wayland or X11 graphical environment.

## References
- https://marc.info/?l=oss-security&m=167879021709955&w=2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28100.json
- https://github.com/flatpak/flatpak/security/advisories/GHSA-7qpw-3vjv-xrqp
- https://nvd.nist.gov/vuln/detail/CVE-2023-28100
- https://security.gentoo.org/glsa/202312-12
- https://github.com/flatpak/flatpak/commit/8e63de9a7d3124f91140fc74f8ca9ed73ed53be9

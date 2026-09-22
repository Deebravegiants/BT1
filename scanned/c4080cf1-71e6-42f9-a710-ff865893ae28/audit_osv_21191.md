# [H] CVE-2021-41133

## Summary
Severity: High
Advisory: CVE-2021-41133
Aliases: GHSA-67h7-w3jq-vh4q
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-08
Source: https://osv.dev/vulnerability/CVE-2021-41133
Type: osv

## Details
Flatpak is a system for building, distributing, and running sandboxed desktop applications on Linux. In versions prior to 1.10.4 and 1.12.0, Flatpak apps with direct access to AF_UNIX sockets such as those used by Wayland, Pipewire or pipewire-pulse can trick portals and other host-OS services into treating the Flatpak app as though it was an ordinary, non-sandboxed host-OS process. They can do this by manipulating the VFS using recent mount-related syscalls that are not blocked by Flatpak's denylist seccomp filter, in order to substitute a crafted `/.flatpak-info` or make that file disappear entirely. Flatpak apps that act as clients for AF_UNIX sockets such as those used by Wayland, Pipewire or pipewire-pulse can escalate the privileges that the corresponding services will believe the Flatpak app has. Note that protocols that operate entirely over the D-Bus session bus (user bus), system bus or accessibility bus are not affected by this. This is due to the use of a proxy process `xdg-dbus-proxy`, whose VFS cannot be manipulated by the Flatpak app, when interacting with these buses. Patches exist for versions 1.10.4 and 1.12.0, and as of time of publication, a patch for version 1.8.2 is being planned. There are no workarounds aside from upgrading to a patched version.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R5656ONDP2MGKIJMKEC7N2NXCV27WGTC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T5DKCYRC6MFSTFCUP4DELCOUUP3SFEFX/
- http://www.openwall.com/lists/oss-security/2021/10/26/9
- https://security.gentoo.org/glsa/202312-12
- https://www.debian.org/security/2021/dsa-4984
- https://github.com/flatpak/flatpak/commit/1330662f33a55e88bfe18e76de28b7922d91a999
- https://github.com/flatpak/flatpak/commit/26b12484eb8a6219b9e7aa287b298a894b2f34ca
- https://github.com/flatpak/flatpak/commit/462fca2c666e0cd2b60d6d2593a7216a83047aaf
- https://github.com/flatpak/flatpak/commit/4c34815784e9ffda5733225c7d95824f96375e36
- https://github.com/flatpak/flatpak/commit/89ae9fe74c6d445bb1b3a40e568d77cf5de47e48
- https://github.com/flatpak/flatpak/commit/9766ee05b1425db397d2cf23afd24c7f6146a69f
- https://github.com/flatpak/flatpak/commit/a10f52a7565c549612c92b8e736a6698a53db330
- https://github.com/flatpak/flatpak/commit/e26ac7586c392b5eb35ff4609fe232c52523b2cf
- https://github.com/flatpak/flatpak/security/advisories/GHSA-67h7-w3jq-vh4q

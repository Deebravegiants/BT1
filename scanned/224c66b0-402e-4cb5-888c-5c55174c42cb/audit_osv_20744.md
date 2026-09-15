# [M] CVE-2021-3658

## Summary
Severity: Medium
Advisory: CVE-2021-3658
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3658
Type: osv

## Details
bluetoothd from bluez incorrectly saves adapters' Discoverable status when a device is powered down, and restores it when powered up. If a device is powered down while discoverable, it will be discoverable when powered on again. This could lead to inadvertent exposure of the bluetooth stack to physically nearby attackers.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00022.html
- https://security.netapp.com/advisory/ntap-20220407-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1984728
- https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=b497b5942a8beb8f89ca1c359c54ad67ec843055
- https://github.com/bluez/bluez/commit/b497b5942a8beb8f89ca1c359c54ad67ec843055
- https://gitlab.gnome.org/GNOME/gnome-bluetooth/-/issues/89

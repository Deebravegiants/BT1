# [C] CVE-2021-43400

## Summary
Severity: Critical
Advisory: CVE-2021-43400
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-11-04
Source: https://osv.dev/vulnerability/CVE-2021-43400
Type: osv

## Details
An issue was discovered in gatt-database.c in BlueZ 5.61. A use-after-free can occur when a client disconnects during D-Bus processing of a WriteValue call.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00022.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00026.html
- https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/?id=838c0dc7641e1c991c0f3027bf94bee4606012f8

# [M] CVE-2021-47055

## Summary
Severity: Medium
Advisory: CVE-2021-47055
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47055
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: require write permissions for locking and badblock ioctls

MEMLOCK, MEMUNLOCK and OTPLOCK modify protection bits. Thus require
write permission. Depending on the hardware MEMLOCK might even be
write-once, e.g. for SPI-NOR flashes with their WP# tied to GND. OTPLOCK
is always write-once.

MEMSETBADBLOCK modifies the bad block table.

## References
- https://git.kernel.org/stable/c/a08799d3e8c8088640956237c183f83463c39668
- https://git.kernel.org/stable/c/077259f5e777c3c8821f6b41dee709fcda27306b
- https://git.kernel.org/stable/c/f4d28d8b9b0e7c4ae04214b8d7e0b0466ec6bcaf
- https://git.kernel.org/stable/c/f73b29819c6314c0ba8b7d5892dfb03487424bee
- https://git.kernel.org/stable/c/1e97743fd180981bef5f01402342bb54bf1c6366
- https://git.kernel.org/stable/c/5880afefe0cb9b2d5e801816acd58bfe91a96981
- https://git.kernel.org/stable/c/75ed985bd6c8ac1d4e673e93ea9d96c9908c1d37
- https://git.kernel.org/stable/c/7b6552719c0ccbbea29dde4be141da54fdb5877e
- https://git.kernel.org/stable/c/9625b00cac6630479c0ff4b9fafa88bee636e1f0

# [M] CVE-2021-47210

## Summary
Severity: Medium
Advisory: CVE-2021-47210
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47210
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: tipd: Remove WARN_ON in tps6598x_block_read

Calling tps6598x_block_read with a higher than allowed len can be
handled by just returning an error. There's no need to crash systems
with panic-on-warn enabled.

## References
- https://git.kernel.org/stable/c/2a897d384513ba7f7ef05611338b9a6ec6aeac00
- https://git.kernel.org/stable/c/2c71811c963b6c310a29455d521d31a7ea6c5b5e
- https://git.kernel.org/stable/c/30dcfcda8992dc42f18e7d35b6a1fa72372d382d
- https://git.kernel.org/stable/c/b7a0a63f3fed57d413bb857de164ea9c3984bc4e
- https://git.kernel.org/stable/c/eff8b7628410cb2eb562ca0d5d1f12e27063733e

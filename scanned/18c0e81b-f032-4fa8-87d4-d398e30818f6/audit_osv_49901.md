# [H] CVE-2019-25162

## Summary
Severity: High
Advisory: CVE-2019-25162
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2019-25162
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: Fix a potential use after free

Free the adap structure only after we are done using it.
This patch just moves the put_device() down a bit to avoid the
use after free.

[wsa: added comment to the code, added Fixes tag]

## References
- https://git.kernel.org/stable/c/871a1e94929a27bf6e2cd99523865c840bbc2d87
- https://git.kernel.org/stable/c/e4c72c06c367758a14f227c847f9d623f1994ecf
- https://git.kernel.org/stable/c/e6412ba3b6508bdf9c074d310bf4144afa6aec1a
- https://git.kernel.org/stable/c/e8e1a046cf87c8b1363e5de835114f2779e2aaf4
- https://git.kernel.org/stable/c/12b0606000d0828630c033bf0c74c748464fe87d
- https://git.kernel.org/stable/c/23a191b132cd87f746c62f3dc27da33683d85829
- https://git.kernel.org/stable/c/35927d7509ab9bf41896b7e44f639504eae08af7
- https://git.kernel.org/stable/c/81cb31756888bb062e92d2dca21cd629d77a46a9

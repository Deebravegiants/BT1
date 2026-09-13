# [H] CVE-2021-47083

## Summary
Severity: High
Advisory: CVE-2021-47083
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47083
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: mediatek: fix global-out-of-bounds issue

When eint virtual eint number is greater than gpio number,
it maybe produce 'desc[eint_n]' size globle-out-of-bounds issue.

## References
- https://git.kernel.org/stable/c/2d5446da5acecf9c67db1c9d55ae2c3e5de01f8d
- https://git.kernel.org/stable/c/441d3873664d170982922c5d2fc01fa89d9439ed
- https://git.kernel.org/stable/c/f373298e1bf0c6ea097c0bcc558dc43ad53e421f
- https://git.kernel.org/stable/c/fb563baa3eb8e7a15f2cff3c2695e2cca0493e69

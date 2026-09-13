# [M] CVE-2021-47257

## Summary
Severity: Medium
Advisory: CVE-2021-47257
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47257
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ieee802154: fix null deref in parse dev addr

Fix a logic error that could result in a null deref if the user sets
the mode incorrectly for the given addr type.

## References
- https://git.kernel.org/stable/c/1f95741981c899c4724647291fec5faa3c777185
- https://git.kernel.org/stable/c/5f728ec65485625e30f46e5b4917ff023ad29ea0
- https://git.kernel.org/stable/c/9fdd04918a452980631ecc499317881c1d120b70
- https://git.kernel.org/stable/c/c6998ccfefa652bac3f9b236821e392af43efa1e
- https://git.kernel.org/stable/c/c7836de2cadd88bc2f20f2c5a3d4ef4c73aef627
- https://git.kernel.org/stable/c/d0f47648b87b6d5f204cb7f3cbce6d36dab85a67
- https://git.kernel.org/stable/c/fdd51e34f45311ab6e48d2147cbc2904731b9993

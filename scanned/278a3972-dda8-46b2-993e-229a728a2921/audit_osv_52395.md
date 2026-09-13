# [H] CVE-2021-47403

## Summary
Severity: High
Advisory: CVE-2021-47403
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47403
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipack: ipoctal: fix module reference leak

A reference to the carrier module was taken on every open but was only
released once when the final reference to the tty struct was dropped.

Fix this by taking the module reference and initialising the tty driver
data when installing the tty.

## References
- https://git.kernel.org/stable/c/7cea848678470daadbfdaa6a112b823c290f900c
- https://git.kernel.org/stable/c/811178f296b16af30264def74c8d2179a72d5562
- https://git.kernel.org/stable/c/9c5b77a7ffc983b2429ce158b50497c5d3c86a69
- https://git.kernel.org/stable/c/bb8a4fcb2136508224c596a7e665bdba1d7c3c27
- https://git.kernel.org/stable/c/c0adb5a947dec6cff7050ec56d78ecd3916f9ce6
- https://git.kernel.org/stable/c/dde4c1429b97383689f755ce92b4ed1e84a9c92b
- https://git.kernel.org/stable/c/31398849b84ebae0d43a1cf379cb9895597f221a
- https://git.kernel.org/stable/c/3253c87e1e5bc0107aab773af2f135ebccf38666

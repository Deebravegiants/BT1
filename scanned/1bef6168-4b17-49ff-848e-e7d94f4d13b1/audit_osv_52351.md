# [H] CVE-2021-47358

## Summary
Severity: High
Advisory: CVE-2021-47358
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47358
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: greybus: uart: fix tty use after free

User space can hold a tty open indefinitely and tty drivers must not
release the underlying structures until the last user is gone.

Switch to using the tty-port reference counter to manage the life time
of the greybus tty state to avoid use after free after a disconnect.

## References
- https://git.kernel.org/stable/c/64062fcaca8872f063ec9da011e7bf30470be33f
- https://git.kernel.org/stable/c/92b67aaafb7c449db9f0c3dcabc0ff967cb3a42d
- https://git.kernel.org/stable/c/92dc0b1f46e12cfabd28d709bb34f7a39431b44f
- https://git.kernel.org/stable/c/9872ff6fdce8b229f01993b611b5d1719cb70ff1
- https://git.kernel.org/stable/c/a5cfd51f6348e8fd7531461366946039c29c7e69
- https://git.kernel.org/stable/c/b9e697e60ce9890e9258a73eb061288e7d68e5e6
- https://git.kernel.org/stable/c/4dc56951a8d9d61d364d346c61a5f1d70b4f5e14

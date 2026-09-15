# [M] CVE-2021-47227

## Summary
Severity: Medium
Advisory: CVE-2021-47227
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47227
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/fpu: Prevent state corruption in __fpu__restore_sig()

The non-compacted slowpath uses __copy_from_user() and copies the entire
user buffer into the kernel buffer, verbatim.  This means that the kernel
buffer may now contain entirely invalid state on which XRSTOR will #GP.
validate_user_xstate_header() can detect some of that corruption, but that
leaves the onus on callers to clear the buffer.

Prior to XSAVES support, it was possible just to reinitialize the buffer,
completely, but with supervisor states that is not longer possible as the
buffer clearing code split got it backwards. Fixing that is possible but
not corrupting the state in the first place is more robust.

Avoid corruption of the kernel XSAVE buffer by using copy_user_to_xstate()
which validates the XSAVE header contents before copying the actual states
to the kernel. copy_user_to_xstate() was previously only called for
compacted-format kernel buffers, but it works for both compacted and
non-compacted forms.

Using it for the non-compacted form is slower because of multiple
__copy_from_user() operations, but that cost is less important than robust
code in an already slow path.

[ Changelog polished by Dave Hansen ]

## References
- https://git.kernel.org/stable/c/ec25ea1f3f05d6f8ee51d1277efea986eafd4f2a
- https://git.kernel.org/stable/c/076f732b16a5bf842686e1b43ab6021a2d98233e
- https://git.kernel.org/stable/c/484cea4f362e1eeb5c869abbfb5f90eae6421b38

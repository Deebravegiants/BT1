# [H] CVE-2021-47291

## Summary
Severity: High
Advisory: CVE-2021-47291
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47291
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix another slab-out-of-bounds in fib6_nh_flush_exceptions

While running the self-tests on a KASAN enabled kernel, I observed a
slab-out-of-bounds splat very similar to the one reported in
commit 821bbf79fe46 ("ipv6: Fix KASAN: slab-out-of-bounds Read in
 fib6_nh_flush_exceptions").

We additionally need to take care of fib6_metrics initialization
failure when the caller provides an nh.

The fix is similar, explicitly free the route instead of calling
fib6_info_release on a half-initialized object.

## References
- https://git.kernel.org/stable/c/115784bcccf135c3a3548098153413d76f16aae0
- https://git.kernel.org/stable/c/830251361425c5be044db4d826aaf304ea3d14c6
- https://git.kernel.org/stable/c/8fb4792f091e608a0a1d353dfdf07ef55a719db5
- https://git.kernel.org/stable/c/ce8fafb68051fba52546f8bbe8621f7641683680

# [H] CVE-2021-47355

## Summary
Severity: High
Advisory: CVE-2021-47355
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47355
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

atm: nicstar: Fix possible use-after-free in nicstar_cleanup()

This module's remove path calls del_timer(). However, that function
does not wait until the timer handler finishes. This means that the
timer handler may still be running after the driver's remove function
has finished, which would result in a use-after-free.

Fix by calling del_timer_sync(), which makes sure the timer handler
has finished, and unable to re-schedule itself.

## References
- https://git.kernel.org/stable/c/2f958b6f6ba0854b39be748d21dfe71e0fe6580f
- https://git.kernel.org/stable/c/4e2a0848ea2cab0716d46f85a8ccd5fa9a493e51
- https://git.kernel.org/stable/c/99779c9d9ffc7775da6f7fd8a7c93ac61657bed5
- https://git.kernel.org/stable/c/bdf5334250c69fabf555b7322c75249ea7d5f148
- https://git.kernel.org/stable/c/34e7434ba4e97f4b85c1423a59b2922ba7dff2ea
- https://git.kernel.org/stable/c/5b991df8881088448cb223e769e37cab8dd40706
- https://git.kernel.org/stable/c/a7a7b2848312cc4c3a42b6e42a8ab2e441857aba
- https://git.kernel.org/stable/c/a7f7c42e31157d1f0871d6a8e1a0b73a6b4ea785
- https://git.kernel.org/stable/c/c471569632654e57c83512e0fc1ba0dbb4544ad6

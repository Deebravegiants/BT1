# [H] Revert "riscv: Define TASK_SIZE_MAX for __access_ok()"

## Summary
Severity: High
Advisory: CVE-2025-38434
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38434
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "riscv: Define TASK_SIZE_MAX for __access_ok()"

This reverts commit ad5643cf2f69 ("riscv: Define TASK_SIZE_MAX for
__access_ok()").

This commit changes TASK_SIZE_MAX to be LONG_MAX to optimize access_ok(),
because the previous TASK_SIZE_MAX (default to TASK_SIZE) requires some
computation.

The reasoning was that all user addresses are less than LONG_MAX, and all
kernel addresses are greater than LONG_MAX. Therefore access_ok() can
filter kernel addresses.

Addresses between TASK_SIZE and LONG_MAX are not valid user addresses, but
access_ok() let them pass. That was thought to be okay, because they are
not valid addresses at hardware level.

Unfortunately, one case is missed: get_user_pages_fast() happily accepts
addresses between TASK_SIZE and LONG_MAX. futex(), for instance, uses
get_user_pages_fast(). This causes the problem reported by Robert [1].

Therefore, revert this commit. TASK_SIZE_MAX is changed to the default:
TASK_SIZE.

This unfortunately reduces performance, because TASK_SIZE is more expensive
to compute compared to LONG_MAX. But correctness first, we can think about
optimization later, if required.

## References
- https://git.kernel.org/stable/c/890ba5be6335dbbbc99af14ea007befb5f83f174
- https://git.kernel.org/stable/c/f8b1898748dfeb4f9b67b6a6d661f354b9de3523
- https://git.kernel.org/stable/c/fe30c30bf3bb68d4a4d8c7c814769857b5c973e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38434.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

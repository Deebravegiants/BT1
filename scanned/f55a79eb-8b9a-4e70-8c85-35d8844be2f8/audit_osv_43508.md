# [H] net: fib_rules: Don't dump dying fib_rule in fib_rules_dump().

## Summary
Severity: High
Advisory: CVE-2026-74288
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74288
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fib_rules: Don't dump dying fib_rule in fib_rules_dump().

rocker_router_fib_event() calls fib_rule_get() during RCU dump.

If the fib_rule is dying, refcount_inc() will complain about it.

Let's call refcount_inc_not_zero() in fib_rules_dump().

## References
- https://git.kernel.org/stable/c/0f929b59f4cd0e05bb1ecefe12b77e85911d4be2
- https://git.kernel.org/stable/c/1fbc6c6efe78f4454a51afa0587efb6826f60f00
- https://git.kernel.org/stable/c/2821e85c058f81c9948a2fb1a634f7b47457d51c
- https://git.kernel.org/stable/c/2dfdc210d240bd48bb2ea746430b02b5571b6db9
- https://git.kernel.org/stable/c/3af0bc1bd9039e2e50abf3e2d7fee411f38bce4e
- https://git.kernel.org/stable/c/4b7ae30c81c2ee10a644749a3704a5c797ccc308
- https://git.kernel.org/stable/c/a7ef30753353ba6a95d693b1863a0214222a199a
- https://git.kernel.org/stable/c/bb4a5b3c91af3c8d705bb2e9f6f8069a70db26fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74288.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

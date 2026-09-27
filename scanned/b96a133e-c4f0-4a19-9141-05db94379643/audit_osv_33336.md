# [H] smc: Use __sk_dst_get() and dst_dev_rcu() in in smc_clc_prfx_set().

## Summary
Severity: High
Advisory: CVE-2025-40139
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40139
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

smc: Use __sk_dst_get() and dst_dev_rcu() in in smc_clc_prfx_set().

smc_clc_prfx_set() is called during connect() and not under RCU
nor RTNL.

Using sk_dst_get(sk)->dev could trigger UAF.

Let's use __sk_dst_get() and dev_dst_rcu() under rcu_read_lock()
after kernel_getsockname().

Note that the returned value of smc_clc_prfx_set() is not used
in the caller.

While at it, we change the 1st arg of smc_clc_prfx_set[46]_rcu()
not to touch dst there.

## References
- https://git.kernel.org/stable/c/0736993bfe5c7a9c744ae3fac62d769dfdae54e1
- https://git.kernel.org/stable/c/5a2fccc4b32c13ddde3676f9e15e1a9baa7d6fde
- https://git.kernel.org/stable/c/80d1fd39f4e37d836655e9f7ffccaf78925049bf
- https://git.kernel.org/stable/c/935d783e5de9b64587f3adb25641dd8385e64ddb
- https://git.kernel.org/stable/c/956c57daba55cf9ed25d9f2512883b8a1a927599
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40139.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

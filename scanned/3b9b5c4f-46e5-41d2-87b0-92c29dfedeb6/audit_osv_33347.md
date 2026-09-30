# [H] smc: Use __sk_dst_get() and dst_dev_rcu() in smc_clc_prfx_match().

## Summary
Severity: High
Advisory: CVE-2025-40168
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40168
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

smc: Use __sk_dst_get() and dst_dev_rcu() in smc_clc_prfx_match().

smc_clc_prfx_match() is called from smc_listen_work() and
not under RCU nor RTNL.

Using sk_dst_get(sk)->dev could trigger UAF.

Let's use __sk_dst_get() and dst_dev_rcu().

Note that the returned value of smc_clc_prfx_match() is not
used in the caller.

## References
- https://git.kernel.org/stable/c/235f81045c008169cc4e1955b4a64e118eebe61b
- https://git.kernel.org/stable/c/326e5cf301d0bec0a672aa834d8254c4f9df6255
- https://git.kernel.org/stable/c/3f119c37aa293af41400cccb3d89fab8dcf774b0
- https://git.kernel.org/stable/c/4f5f52a5842937f945582a93cb9daed9ea526fee
- https://git.kernel.org/stable/c/d26e80f7fb62d77757b67a1b94e4ac756bc9c658
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40168.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40168
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

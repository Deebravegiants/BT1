# [H] net/sched: fix use-after-free in taprio_dev_notifier

## Summary
Severity: High
Advisory: CVE-2025-38087
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-30
Source: https://osv.dev/vulnerability/CVE-2025-38087
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: fix use-after-free in taprio_dev_notifier

Since taprio’s taprio_dev_notifier() isn’t protected by an
RCU read-side critical section, a race with advance_sched()
can lead to a use-after-free.

Adding rcu_read_lock() inside taprio_dev_notifier() prevents this.

## References
- https://git.kernel.org/stable/c/8a008c89e5e5c5332e4c0a33d707db9ddd529f8a
- https://git.kernel.org/stable/c/8c5713ce1ced75f9e9ed5c642ea3d2ba06ead69c
- https://git.kernel.org/stable/c/b1547d28ba468bc3b88764efd13e4319bab63be8
- https://git.kernel.org/stable/c/b160766e26d4e2e2d6fe2294e0b02f92baefcec5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38087.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

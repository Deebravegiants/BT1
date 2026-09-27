# [H] netdev: prevent accessing NAPI instances from another namespace

## Summary
Severity: High
Advisory: CVE-2025-21659
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2025-21659
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netdev: prevent accessing NAPI instances from another namespace

The NAPI IDs were not fully exposed to user space prior to the netlink
API, so they were never namespaced. The netlink API must ensure that
at the very least NAPI instance belongs to the same netns as the owner
of the genl sock.

napi_by_id() can become static now, but it needs to move because of
dev_get_by_napi_id().

## References
- https://git.kernel.org/stable/c/b683ba0df11ff563cc237eb1b74d6adfa77226bf
- https://git.kernel.org/stable/c/d1cacd74776895f6435941f86a1130e58f6dd226
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21659.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21659
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

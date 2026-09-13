# [H] mptcp: pm: only decrement add_addr_accepted for MPJ req

## Summary
Severity: High
Advisory: CVE-2024-45009
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45009
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.167, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: pm: only decrement add_addr_accepted for MPJ req

Adding the following warning ...

  WARN_ON_ONCE(msk->pm.add_addr_accepted == 0)

... before decrementing the add_addr_accepted counter helped to find a
bug when running the "remove single subflow" subtest from the
mptcp_join.sh selftest.

Removing a 'subflow' endpoint will first trigger a RM_ADDR, then the
subflow closure. Before this patch, and upon the reception of the
RM_ADDR, the other peer will then try to decrement this
add_addr_accepted. That's not correct because the attached subflows have
not been created upon the reception of an ADD_ADDR.

A way to solve that is to decrement the counter only if the attached
subflow was an MP_JOIN to a remote id that was not 0, and initiated by
the host receiving the RM_ADDR.

## References
- https://git.kernel.org/stable/c/1c1f721375989579e46741f59523e39ec9b2a9bd
- https://git.kernel.org/stable/c/2060f1efab370b496c4903b840844ecaff324c3c
- https://git.kernel.org/stable/c/35b31f5549ede4070566b949781e83495906b43d
- https://git.kernel.org/stable/c/85b866e4c4e63a1d7afb58f1e24273caad03d0b7
- https://git.kernel.org/stable/c/d20bf2c96d7ffd171299b32f562f70e5bf5dc608
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45009.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45009
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

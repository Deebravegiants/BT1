# [H] net: hns3: fix kernel crash problem in concurrent scenario

## Summary
Severity: High
Advisory: CVE-2024-39507
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39507
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: fix kernel crash problem in concurrent scenario

When link status change, the nic driver need to notify the roce
driver to handle this event, but at this time, the roce driver
may uninit, then cause kernel crash.

To fix the problem, when link status change, need to check
whether the roce registered, and when uninit, need to wait link
update finish.

## References
- https://git.kernel.org/stable/c/12cda920212a49fa22d9e8b9492ac4ea013310a4
- https://git.kernel.org/stable/c/62b5dfb67bfa8bd0301bf3442004563495f9ee48
- https://git.kernel.org/stable/c/689de7c3bfc7d47e0eacc641c4ce4a0f579aeefa
- https://git.kernel.org/stable/c/6d0007f7b69d684879a0f598a042e40244d3cf63
- https://git.kernel.org/stable/c/b2c5024b771cd1dd8175d5f6949accfadbab7edd
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39507.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39507
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

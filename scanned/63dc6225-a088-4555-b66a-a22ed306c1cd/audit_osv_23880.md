# [M] power/reset: arm-versatile: Fix refcount leak in versatile_reboot_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49609
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49609
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

power/reset: arm-versatile: Fix refcount leak in versatile_reboot_probe

of_find_matching_node_and_match() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/493ceca3271316e74639c89ff8ac35883de64256
- https://git.kernel.org/stable/c/49fa778ee044b00471dd9ccae5f6a121fffea1ac
- https://git.kernel.org/stable/c/6689754b121bd487f99680280102b3a5cd7374af
- https://git.kernel.org/stable/c/71ab83ac65e2d671552374123bf920c1d698335a
- https://git.kernel.org/stable/c/78bdf732cf5d74d1c6ecda06830a91f80a4aef6f
- https://git.kernel.org/stable/c/80192eff64eee9b3bc0594a47381937b94b9d65a
- https://git.kernel.org/stable/c/a9ed3ad3a8d1dfbc829d86edb3236873a315db11
- https://git.kernel.org/stable/c/b4d224eec96a18fa8959512cd9e5b6a50bd16a41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49609.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49609
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] phonet/pep: fix racy skb_queue_empty() use

## Summary
Severity: Medium
Advisory: CVE-2024-27402
Ecosystem: Linux
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27402
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <5.15.181, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

phonet/pep: fix racy skb_queue_empty() use

The receive queues are protected by their respective spin-lock, not
the socket lock. This could lead to skb_peek() unexpectedly
returning NULL or a pointer to an already dequeued socket buffer.

## References
- https://git.kernel.org/stable/c/0a9f558c72c47472c38c05fcb72c70abb9104277
- https://git.kernel.org/stable/c/7d2a894d7f487dcb894df023e9d3014cf5b93fe5
- https://git.kernel.org/stable/c/7d3914a477eed92b48c493a8631cc4554ab4fd4f
- https://git.kernel.org/stable/c/8ef4fcc7014b9f93619851d6b78d6cc2789a4c88
- https://git.kernel.org/stable/c/9d5523e065b568e79dfaa2ea1085a5bcf74baf78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27402.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27402
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] virtio/vsock: Improve MSG_ZEROCOPY error handling

## Summary
Severity: Medium
Advisory: CVE-2024-53117
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53117
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio/vsock: Improve MSG_ZEROCOPY error handling

Add a missing kfree_skb() to prevent memory leaks.

## References
- https://git.kernel.org/stable/c/50061d7319e21165d04e3024354c1b43b6137821
- https://git.kernel.org/stable/c/60cf6206a1f513512f5d73fa4d3dbbcad2e7dcd6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53117.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

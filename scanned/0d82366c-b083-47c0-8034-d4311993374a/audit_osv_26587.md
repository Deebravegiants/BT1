# [H] Bluetooth: hci_conn: fail SCO/ISO via hci_conn_failed if ACL gone early

## Summary
Severity: High
Advisory: CVE-2023-53374
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53374
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_conn: fail SCO/ISO via hci_conn_failed if ACL gone early

Not calling hci_(dis)connect_cfm before deleting conn referred to by a
socket generally results to use-after-free.

When cleaning up SCO connections when the parent ACL is deleted too
early, use hci_conn_failed to do the connection cleanup properly.

We also need to clean up ISO connections in a similar situation when
connecting has started but LE Create CIS is not yet sent, so do it too
here.

## References
- https://git.kernel.org/stable/c/3344d318337d9dca928fd448e966557ec5063f85
- https://git.kernel.org/stable/c/397d58007532644b35fad746da48c41161f32a57
- https://git.kernel.org/stable/c/e94b898463a62b72a2a8b75dea8936bf4db78e00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53374.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

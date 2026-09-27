# [H] xsk: recycle buffer in case Rx queue was full

## Summary
Severity: High
Advisory: CVE-2024-35834
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35834
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: recycle buffer in case Rx queue was full

Add missing xsk_buff_free() call when __xsk_rcv_zc() failed to produce
descriptor to XSK Rx queue.

## References
- https://git.kernel.org/stable/c/269009893146c495f41e9572dd9319e787c2eba9
- https://git.kernel.org/stable/c/7b4d93d31aade99210d41cd9d4cbd2957c98bc8c
- https://git.kernel.org/stable/c/cce713664548284daf977739e7ff1cd59e84189c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35834.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35834
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

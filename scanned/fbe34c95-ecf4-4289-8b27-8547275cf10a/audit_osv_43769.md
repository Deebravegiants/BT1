# [H] xsk: validate launch-time metadata size

## Summary
Severity: High
Advisory: CVE-2026-74708
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74708
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: validate launch-time metadata size

Launch-time metadata extends beyond the first 16 bytes of struct
xsk_tx_metadata. Reject the request when the registered metadata area does
not contain the complete field.

Snapshot the validated flags for the generic transmit path and use that
snapshot for request and completion processing, avoiding inconsistent
decisions if user space changes the flags concurrently.

Note that only xsk_skb_metadata is properly using the flags,
__xsk_buff_get_metadata ignores them. Next commits address that.

## References
- https://git.kernel.org/stable/c/439ce2dddf3d22129b9113a7881637256a35e936
- https://git.kernel.org/stable/c/af511afa1d2977f384044df78d6fbf9fba653f7a
- https://git.kernel.org/stable/c/bc63d47611c07b0d5d655fe1a590861931527920
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74708.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74708
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

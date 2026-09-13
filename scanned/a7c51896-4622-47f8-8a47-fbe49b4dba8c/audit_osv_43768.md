# [H] xsk: validate metadata when processing requests

## Summary
Severity: High
Advisory: CVE-2026-74707
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74707
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: validate metadata when processing requests

The zero-copy path validates TX metadata while obtaining the descriptor
context, then reads it again later when preparing the hardware request.
User space can change the metadata between those operations and bypass the
original validation.

Validate the metadata in xsk_tx_metadata_request() and use the resulting
flags snapshot for every feature check. Read request fields once so all
zero-copy drivers process only values observed after successful
validation.

## References
- https://git.kernel.org/stable/c/0cc7aa6e0d19027fdd42e6fbd156267ac1e3bbba
- https://git.kernel.org/stable/c/5fd121971912dee2f5af1efec64462ac722deb17
- https://git.kernel.org/stable/c/849b1664dbda1cf6c63e0fd4f9dec23782b8c851
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74707.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74707
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

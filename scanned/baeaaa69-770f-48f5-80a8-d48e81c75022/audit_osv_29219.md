# [H] RDMA/rxe: Fix responder length checking for UD request packets

## Summary
Severity: High
Advisory: CVE-2024-40992
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40992
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix responder length checking for UD request packets

According to the IBA specification:
If a UD request packet is detected with an invalid length, the request
shall be an invalid request and it shall be silently dropped by
the responder. The responder then waits for a new request packet.

commit 689c5421bfe0 ("RDMA/rxe: Fix incorrect responder length checking")
defers responder length check for UD QPs in function `copy_data`.
But it introduces a regression issue for UD QPs.

When the packet size is too large to fit in the receive buffer.
`copy_data` will return error code -EINVAL. Then `send_data_in`
will return RESPST_ERR_MALFORMED_WQE. UD QP will transfer into
ERROR state.

## References
- https://git.kernel.org/stable/c/163868ec1f6c610d16da9e458fe1dd7d5de97341
- https://git.kernel.org/stable/c/943c94f41dfe36536dc9aaa12c9efdf548ceb996
- https://git.kernel.org/stable/c/f67ac0061c7614c1548963d3ef1ee1606efd8636
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40992.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40992
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

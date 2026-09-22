# [H] Bluetooth: L2CAP: Fix stack-out-of-bounds read in l2cap_ecred_conn_req

## Summary
Severity: High
Advisory: CVE-2026-31513
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31513
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.75 <6.12.80, >=6.18.16 <6.18.21, >=6.19.6 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: Fix stack-out-of-bounds read in l2cap_ecred_conn_req

Syzbot reported a KASAN stack-out-of-bounds read in l2cap_build_cmd()
that is triggered by a malformed Enhanced Credit Based Connection Request.

The vulnerability stems from l2cap_ecred_conn_req(). The function allocates
a local stack buffer (`pdu`) designed to hold a maximum of 5 Source Channel
IDs (SCIDs), totaling 18 bytes. When an attacker sends a request with more
than 5 SCIDs, the function calculates `rsp_len` based on this unvalidated
`cmd_len` before checking if the number of SCIDs exceeds
L2CAP_ECRED_MAX_CID.

If the SCID count is too high, the function correctly jumps to the
`response` label to reject the packet, but `rsp_len` retains the
attacker's oversized value. Consequently, l2cap_send_cmd() is instructed
to read past the end of the 18-byte `pdu` buffer, triggering a
KASAN panic.

Fix this by moving the assignment of `rsp_len` to after the `num_scid`
boundary check. If the packet is rejected, `rsp_len` will safely
remain 0, and the error response will only read the 8-byte base header
from the stack.

## References
- https://git.kernel.org/stable/c/5b35f8211a913cfe7ab9d54fa36a272d2059a588
- https://git.kernel.org/stable/c/9d87cb22195b2c67405f5485d525190747ad5493
- https://git.kernel.org/stable/c/a3d9c50d69785ae02e153f000da1b5fd6dbfdf1b
- https://git.kernel.org/stable/c/c8e1a27edb8b4e5afb56b384acd7b6c2dec1b7cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31513.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31513
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

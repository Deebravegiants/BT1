# [C] ksmbd: fix signededness bug in smb_direct_prepare_negotiation()

## Summary
Severity: Critical
Advisory: CVE-2026-43185
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43185
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix signededness bug in smb_direct_prepare_negotiation()

smb_direct_prepare_negotiation() casts an unsigned __u32 value
from sp->max_recv_size and req->preferred_send_size to a signed
int before computing min_t(int, ...). A maliciously provided
preferred_send_size of 0x80000000 will return as smaller than
max_recv_size, and then be used to set the maximum allowed
alowed receive size for the next message.

By sending a second message with a large value (>1420 bytes)
the attacker can then achieve a heap buffer overflow.

This fix replaces min_t(int, ...) with min_t(u32)

## References
- https://git.kernel.org/stable/c/55abc475d096da4a5356b6efb0cfdc6156bc1550
- https://git.kernel.org/stable/c/6b4f875aac344cdd52a1f34cc70ed2f874a65757
- https://git.kernel.org/stable/c/ceae058eb707ddd0d68f0872f9d9f23b7c30c37b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43185.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43185
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

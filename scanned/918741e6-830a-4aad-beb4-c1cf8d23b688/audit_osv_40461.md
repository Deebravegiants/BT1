# [H] Bluetooth: RFCOMM: validate skb length in MCC handlers

## Summary
Severity: High
Advisory: CVE-2026-53254
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53254
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: RFCOMM: validate skb length in MCC handlers

The RFCOMM MCC handlers cast skb->data to protocol-specific structs
without validating skb->len first. A malicious remote device can send
truncated MCC frames and trigger out-of-bounds reads in these handlers.

Fix this by using skb_pull_data() to validate and access the required
data before dereferencing it.

rfcomm_recv_rpn() requires special handling since ETSI TS 07.10 allows
1-byte RPN requests. Handle this by validating only the DLCI byte first,
and validating the full struct only when len > 1.

## References
- https://git.kernel.org/stable/c/08b9c1fbe78f4ad3f6250c6541cfaabdbeb81997
- https://git.kernel.org/stable/c/0d637136ce89f9a2309b2c3502402ce400dab0ef
- https://git.kernel.org/stable/c/1b070ac9e99c2c2c3a8112943ca98ab6fca7f10c
- https://git.kernel.org/stable/c/23882b828c3c8c51d0c946446a396b10abb3b16b
- https://git.kernel.org/stable/c/3eabc6d47a0ad22b053329997aaf0ec1e581e392
- https://git.kernel.org/stable/c/7c15c7c2878957cbfed93bcc29c13fdace464254
- https://git.kernel.org/stable/c/98377e6b1a1a56561ec66a181573ea2b61b2079e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53254.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53254
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

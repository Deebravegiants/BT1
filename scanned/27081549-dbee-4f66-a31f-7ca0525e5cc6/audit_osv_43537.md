# [H] wifi: wcn36xx: fix OOB read from firmware count in PRINT_REG_INFO indication

## Summary
Severity: High
Advisory: CVE-2026-74340
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74340
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wcn36xx: fix OOB read from firmware count in PRINT_REG_INFO indication

The firmware-controlled rsp->count field is used as the loop bound for
indexing into the flexible rsp->regs[] array without validation against
the message length. A count exceeding the actual data causes out-of-
bounds reads from the heap-allocated message buffer.

Add a check that count fits within the received message.

## References
- https://git.kernel.org/stable/c/0907c06dccae9e3c8d5a68eb9014beec73a36e79
- https://git.kernel.org/stable/c/22b0b8572a64362531dd0ed499b75e16282aeb2b
- https://git.kernel.org/stable/c/23d210877968657bd07e1a517e0b516db20a1d80
- https://git.kernel.org/stable/c/3cf92b44c4fb88a5e8de8733a4494c0956606bca
- https://git.kernel.org/stable/c/64228dfc4247aca178c01e5a37af7d8dcc7a6089
- https://git.kernel.org/stable/c/df2187acfca6c6cca372c5d35f42394d9c270b09
- https://git.kernel.org/stable/c/f03782f7f41f2afee5076a1ef08ced5649218771
- https://git.kernel.org/stable/c/f987efff29a5fe45320ea5991c9d5cb98b676953
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74340.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

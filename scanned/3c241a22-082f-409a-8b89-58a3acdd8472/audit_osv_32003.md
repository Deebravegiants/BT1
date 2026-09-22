# [C] netfilter: nfnetlink_queue: Initialize ctx to avoid memory allocation error

## Summary
Severity: Critical
Advisory: CVE-2025-22110
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22110
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_queue: Initialize ctx to avoid memory allocation error

It is possible that ctx in nfqnl_build_packet_message() could be used
before it is properly initialize, which is only initialized
by nfqnl_get_sk_secctx().

This patch corrects this problem by initializing the lsmctx to a safe
value when it is declared.

This is similar to the commit 35fcac7a7c25
("audit: Initialize lsmctx to avoid memory allocation error").

## References
- https://git.kernel.org/stable/c/778b09d91baafb13408470c721d034d6515cfa5a
- https://git.kernel.org/stable/c/ddbf7e1d82a1d0c1d3425931a6cb1b83f8454759
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22110.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

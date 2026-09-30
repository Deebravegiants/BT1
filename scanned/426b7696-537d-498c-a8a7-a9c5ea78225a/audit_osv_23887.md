# [H] netfilter: nf_tables: avoid skb access on nf_stolen

## Summary
Severity: High
Advisory: CVE-2022-49622
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49622
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: avoid skb access on nf_stolen

When verdict is NF_STOLEN, the skb might have been freed.

When tracing is enabled, this can result in a use-after-free:
1. access to skb->nf_trace
2. access to skb->mark
3. computation of trace id
4. dump of packet payload

To avoid 1, keep a cached copy of skb->nf_trace in the
trace state struct.
Refresh this copy whenever verdict is != STOLEN.

Avoid 2 by skipping skb->mark access if verdict is STOLEN.

3 is avoided by precomputing the trace id.

Only dump the packet when verdict is not "STOLEN".

## References
- https://git.kernel.org/stable/c/0016d5d46d7440729a3132f61a8da3bf7f84e2ba
- https://git.kernel.org/stable/c/e34b9ed96ce3b06c79bf884009b16961ca478f87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49622.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49622
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

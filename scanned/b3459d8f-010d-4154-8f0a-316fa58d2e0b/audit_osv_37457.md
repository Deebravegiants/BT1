# [H] rxrpc: Fix use of wrong skb when comparing queued RESP challenge serial

## Summary
Severity: High
Advisory: CVE-2026-31640
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31640
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix use of wrong skb when comparing queued RESP challenge serial

In rxrpc_post_response(), the code should be comparing the challenge serial
number from the cached response before deciding to switch to a newer
response, but looks at the newer packet private data instead, rendering the
comparison always false.

Fix this by switching to look at the older packet.

Fix further[1] to substitute the new packet in place of the old one if
newer and also to release whichever we don't use.

## References
- https://git.kernel.org/stable/c/20386e7f8d97475b8d815873e246423317ec4260
- https://git.kernel.org/stable/c/9132b1a7bf83b4a8042fffbc99d075b727a16742
- https://git.kernel.org/stable/c/b33f5741bb187db8ff32e8f5b96def77cc94dfca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31640.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31640
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

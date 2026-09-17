# [H] rxrpc: Fix untrusted unsigned subtract

## Summary
Severity: High
Advisory: CVE-2025-39962
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39962
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix untrusted unsigned subtract

Fix the following Smatch static checker warning:

   net/rxrpc/rxgk_app.c:65 rxgk_yfs_decode_ticket()
   warn: untrusted unsigned subtract. 'ticket_len - 10 * 4'

by prechecking the length of what we're trying to extract in two places in
the token and decoding for a response packet.

Also use sizeof() on the struct we're extracting rather specifying the size
numerically to be consistent with the other related statements.

## References
- https://git.kernel.org/stable/c/2429a197648178cd4dc930a9d87c13c547460564
- https://git.kernel.org/stable/c/71571e187106631a8127f2dde780f35caa358d33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39962.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39962
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

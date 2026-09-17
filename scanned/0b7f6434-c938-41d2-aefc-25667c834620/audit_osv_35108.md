# [H] io_uring/zctx: check chained notif contexts

## Summary
Severity: High
Advisory: CVE-2025-68317
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68317
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/zctx: check chained notif contexts

Send zc only links ubuf_info for requests coming from the same context.
There are some ambiguous syz reports, so let's check the assumption on
notification completion.

## References
- https://git.kernel.org/stable/c/aaafd17d3f4be2c15539359a5b4bfa00237f687f
- https://git.kernel.org/stable/c/ab3ea6eac5f45669b091309f592c4ea324003053
- https://git.kernel.org/stable/c/d664a3ce3a604231a0b144c152a3755d03b18b60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68317.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

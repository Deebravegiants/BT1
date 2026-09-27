# [H] ksmbd: fix potential use-after-free in oplock/lease break ack

## Summary
Severity: High
Advisory: CVE-2025-38437
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38437
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix potential use-after-free in oplock/lease break ack

If ksmbd_iov_pin_rsp return error, use-after-free can happen by
accessing opinfo->state and opinfo_put and ksmbd_fd_put could
called twice.

## References
- https://git.kernel.org/stable/c/50f930db22365738d9387c974416f38a06e8057e
- https://git.kernel.org/stable/c/8106adc21a2270c16abf69cd74ccd7c79c6e7acd
- https://git.kernel.org/stable/c/815f1161d6dbc4c54ccf94b7d3fdeab34b4d7477
- https://git.kernel.org/stable/c/97c355989928a5f60b228ef5266c1be67a46cdf9
- https://git.kernel.org/stable/c/e38ec88a2b42c494601b1213816d75f0b54d9bf0
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38437.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38437
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

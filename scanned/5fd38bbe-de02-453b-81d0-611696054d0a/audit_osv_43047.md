# [H] afs: Fix callback service message parsers to pass through -EAGAIN

## Summary
Severity: High
Advisory: CVE-2026-72374
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72374
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix callback service message parsers to pass through -EAGAIN

The AFS filesystem client uses an rxrpc server to listen for callback
notifications.  Each callback call type handler has a delivery function
that parses the incoming request stream, and this should return -EAGAIN the
last packet hasn't yet been seen, but all currently queued received data is
consumed.  afs_extract_data() does this, but the -EAGAIN return is switched
to 0 inadvertantly

Fix callback service message parsers to pass through -EAGAIN

## References
- https://git.kernel.org/stable/c/09c67a7ded481482155b836c8c7f078a3075f8de
- https://git.kernel.org/stable/c/0acbc09d2aca0432af45cec114f20d55ceafaec4
- https://git.kernel.org/stable/c/0f36469d7ce98b362934113c550d08bb0c784231
- https://git.kernel.org/stable/c/239cd337c9d047e7097f5b2ebbb41ddfb8180bc6
- https://git.kernel.org/stable/c/26b737b3769e92493fe94c34620399d93ca231ae
- https://git.kernel.org/stable/c/5a39b145a8fb49f316e7ec1f29ba51d68095c7e4
- https://git.kernel.org/stable/c/772850871a2e772e26f9d93f1e9ddd413b3eeaa4
- https://git.kernel.org/stable/c/f14dd036fad3d359f26f1282199cec06b3a9362b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72374.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72374
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

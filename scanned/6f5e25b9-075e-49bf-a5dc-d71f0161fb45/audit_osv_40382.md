# [H] ppp: require CAP_NET_ADMIN in target netns for unattached ioctls

## Summary
Severity: High
Advisory: CVE-2026-53075
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53075
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ppp: require CAP_NET_ADMIN in target netns for unattached ioctls

/dev/ppp open is currently authorized against file->f_cred->user_ns,
while unattached administrative ioctls operate on current->nsproxy->net_ns.

As a result, a local unprivileged user can create a new user namespace
with CLONE_NEWUSER, gain CAP_NET_ADMIN only in that new user namespace,
and still issue PPPIOCNEWUNIT, PPPIOCATTACH, or PPPIOCATTCHAN against
an inherited network namespace.

Require CAP_NET_ADMIN in the user namespace that owns the target network
namespace before handling unattached PPP administrative ioctls.

This preserves normal pppd operation in the network namespace it is
actually privileged in, while rejecting the userns-only inherited-netns
case.

## References
- https://git.kernel.org/stable/c/1a8a51ce85075a56a743b6f142606dd2696a391c
- https://git.kernel.org/stable/c/2bb6379416fd19f44c3423a00bfd8626259f6067
- https://git.kernel.org/stable/c/3b2c2157dc2afc5c17cd7238afefca92f1ef330e
- https://git.kernel.org/stable/c/5013be175c7ffd8b39efbc3c9c4db5b10b85fea8
- https://git.kernel.org/stable/c/5080e188c914110034bbc569d5cfa2f06204681d
- https://git.kernel.org/stable/c/67e901e28d177ac9a9bed76d69ce3471e704a89e
- https://git.kernel.org/stable/c/954745d0223e7caec917c0b2d1a889ff56fa6e54
- https://git.kernel.org/stable/c/c9edd90c57ae23692fff6b049fdfa4572a9fd532
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

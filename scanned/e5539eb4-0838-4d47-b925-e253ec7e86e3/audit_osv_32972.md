# [H] atm: clip: Fix potential null-ptr-deref in to_atmarpd().

## Summary
Severity: High
Advisory: CVE-2025-38460
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38460
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.296, >=5.5.0 <5.10.240, >=5.11.0 <5.15.189, >=5.16.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

atm: clip: Fix potential null-ptr-deref in to_atmarpd().

atmarpd is protected by RTNL since commit f3a0592b37b8 ("[ATM]: clip
causes unregister hang").

However, it is not enough because to_atmarpd() is called without RTNL,
especially clip_neigh_solicit() / neigh_ops->solicit() is unsleepable.

Also, there is no RTNL dependency around atmarpd.

Let's use a private mutex and RCU to protect access to atmarpd in
to_atmarpd().

## References
- https://git.kernel.org/stable/c/06935c50cfa3ac57cce80bba67b6d38ec1406e92
- https://git.kernel.org/stable/c/3251ce3979f41bd228f77a7615f9dd616d06a110
- https://git.kernel.org/stable/c/36caab990b69ef4eec1d81c52a19f080b7daa059
- https://git.kernel.org/stable/c/706cc36477139c1616a9b2b96610a8bb520b7119
- https://git.kernel.org/stable/c/70eac9ba7ce25d99c1d99bbf4ddb058940f631f9
- https://git.kernel.org/stable/c/a4c5785feb979cd996a99cfaad8bf353b2e79301
- https://git.kernel.org/stable/c/ee4d9e4ddf3f9c4ee2ec0a3aad6196ee36d30e57
- https://git.kernel.org/stable/c/f58e4270c73e7f086322978d585ea67c8076ce49
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38460.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38460
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

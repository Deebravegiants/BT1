# [H] smb: client: harden POSIX SID length parsing

## Summary
Severity: High
Advisory: CVE-2026-64380
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64380
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: harden POSIX SID length parsing

posix_info_sid_size() reads sid[1] to obtain the subauthority count,
but its existing boundary check still accepts buffers with only one
remaining byte. Require two bytes before reading sid[1] so all client
paths that reuse the helper reject truncated POSIX SIDs safely.

## References
- https://git.kernel.org/stable/c/0de5b8e76847f5de26f364a82c6602c4881c30da
- https://git.kernel.org/stable/c/171605aed68380c2fa75dff9b3a1ed427c50065b
- https://git.kernel.org/stable/c/4213c1208978483021d7d125c131de3985d38f61
- https://git.kernel.org/stable/c/427eb7eb46425fec845a43e861f3d6e2899cae59
- https://git.kernel.org/stable/c/46a84715a015cb48e1b9c219dc88c03d8a541ea4
- https://git.kernel.org/stable/c/7ad2bcf2441430bb2e918fb3ef9a90d775a6e422
- https://git.kernel.org/stable/c/86c5d470f5d42e61123b2f4b4f0b91f4eee5b980
- https://git.kernel.org/stable/c/96e889bc1e759c83f25093e8c2f3da31b4973f30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64380.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64380
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

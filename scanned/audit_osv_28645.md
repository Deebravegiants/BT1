# [H] media: tc358743: register v4l2 async device only after successful setup

## Summary
Severity: High
Advisory: CVE-2024-35830
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35830
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: tc358743: register v4l2 async device only after successful setup

Ensure the device has been setup correctly before registering the v4l2
async device, thus allowing userspace to access.

## References
- https://git.kernel.org/stable/c/17c2650de14842c25c569cbb2126c421489a3a24
- https://git.kernel.org/stable/c/4f1490a5d7a0472ee5d9f36547bc4ba46be755c7
- https://git.kernel.org/stable/c/610f20e5cf35ca9c0992693cae0dd8643ce932e7
- https://git.kernel.org/stable/c/87399f1ff92203d65f1febf5919429f4bb613a02
- https://git.kernel.org/stable/c/8ba8db9786b55047df5ad3db3e01dd886687a77d
- https://git.kernel.org/stable/c/b8505a1aee8f1edc9d16d72ae09c93de086e2a1a
- https://git.kernel.org/stable/c/c915c46a25c3efb084c4f5e69a053d7f7a635496
- https://git.kernel.org/stable/c/daf21394f9898fb9f0698c3e50de08132d2164e6
- https://git.kernel.org/stable/c/edbb3226c985469a2f8eb69885055c9f5550f468
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35830.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35830
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] media: dvbdev: adopts refcnt to avoid UAF

## Summary
Severity: High
Advisory: CVE-2022-50274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50274
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvbdev: adopts refcnt to avoid UAF

dvb_unregister_device() is known that prone to use-after-free.
That is, the cleanup from dvb_unregister_device() releases the dvb_device
even if there are pointers stored in file->private_data still refer to it.

This patch adds a reference counter into struct dvb_device and delays its
deallocation until no pointer refers to the object.

## References
- https://git.kernel.org/stable/c/0fc044b2b5e2d05a1fa1fb0d7f270367a7855d79
- https://git.kernel.org/stable/c/219b44bf94203bd433aa91b7796475bf656348e5
- https://git.kernel.org/stable/c/2abd73433872194bccdf1432a0980e4ec5273c2a
- https://git.kernel.org/stable/c/6d18b44bb44e1f4d97dfe0efe92ac0f0984739c2
- https://git.kernel.org/stable/c/88a6f8a72d167294c0931c7874941bf37a41b6dd
- https://git.kernel.org/stable/c/9945d05d6693710574f354c5dbddc47f5101eb77
- https://git.kernel.org/stable/c/a2f0a08aa613176c9688c81d7b598a7779974991
- https://git.kernel.org/stable/c/ac521bbe3d00fa574e66a9361763f2b37725bc97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50274.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

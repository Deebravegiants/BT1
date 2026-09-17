# [H] bus: mhi: host: Fix race between unprepare and queue_buf

## Summary
Severity: High
Advisory: CVE-2025-23151
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23151
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.8.0 <6.13.12, >=6.13.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: mhi: host: Fix race between unprepare and queue_buf

A client driver may use mhi_unprepare_from_transfer() to quiesce
incoming data during the client driver's tear down. The client driver
might also be processing data at the same time, resulting in a call to
mhi_queue_buf() which will invoke mhi_gen_tre(). If mhi_gen_tre() runs
after mhi_unprepare_from_transfer() has torn down the channel, a panic
will occur due to an invalid dereference leading to a page fault.

This occurs because mhi_gen_tre() does not verify the channel state
after locking it. Fix this by having mhi_gen_tre() confirm the channel
state is valid, or return error to avoid accessing deinitialized data.

[mani: added stable tag]

## References
- https://git.kernel.org/stable/c/0686a818d77a431fc3ba2fab4b46bbb04e8c9380
- https://git.kernel.org/stable/c/178e5657c8fd285125cc6743a81b513bce099760
- https://git.kernel.org/stable/c/3e7ecf181cbdde9753204ada3883ca1704d8702b
- https://git.kernel.org/stable/c/5f084993c90d9d0b4a52a349ede5120f992a7ca1
- https://git.kernel.org/stable/c/899d0353ea69681f474b6bc9de32c663b89672da
- https://git.kernel.org/stable/c/a77955f7704b2a00385e232cbcc1cb06b5c7a425
- https://git.kernel.org/stable/c/ee1fce83ed56450087309b9b74ad9bcb2b010fa6
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23151.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23151
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

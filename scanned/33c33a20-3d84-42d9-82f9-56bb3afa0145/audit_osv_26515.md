# [H] Bluetooth: L2CAP: fix "bad unlock balance" in l2cap_disconnect_rsp

## Summary
Severity: High
Advisory: CVE-2023-53297
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53297
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: fix "bad unlock balance" in l2cap_disconnect_rsp

conn->chan_lock isn't acquired before l2cap_get_chan_by_scid,
if l2cap_get_chan_by_scid returns NULL, then 'bad unlock balance'
is triggered.

## References
- https://git.kernel.org/stable/c/116b9c002c894097adc2b8684db2d1da4229ed46
- https://git.kernel.org/stable/c/2112c4c47d36bc5aba3ddeb9afedce6ae6a67e7d
- https://git.kernel.org/stable/c/25e97f7b1866e6b8503be349eeea44bb52d661ce
- https://git.kernel.org/stable/c/5134556c9be582793f30695c09d18a26fe1ff2d7
- https://git.kernel.org/stable/c/55410a9144c76ecda126e6cdec556dfcd8f343b2
- https://git.kernel.org/stable/c/5f352a56f0e607e6ff539cbf12156bfd8af232be
- https://git.kernel.org/stable/c/6a27762340ad08643de3bc17fe1646ea489ca2e2
- https://git.kernel.org/stable/c/fd269a0435f8e9943b7a57c5a59688848d42d449
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53297.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53297
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

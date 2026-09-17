# [M] media: az6007: Fix null-ptr-deref in az6007_i2c_xfer()

## Summary
Severity: Medium
Advisory: CVE-2023-53220
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53220
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.197, >=5.11.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: az6007: Fix null-ptr-deref in az6007_i2c_xfer()

In az6007_i2c_xfer, msg is controlled by user. When msg[i].buf
is null and msg[i].len is zero, former checks on msg[i].buf would be
passed. Malicious data finally reach az6007_i2c_xfer. If accessing
msg[i].buf[0] without sanity check, null ptr deref would happen.
We add check on msg[i].len to prevent crash.

Similar commit:
commit 0ed554fd769a
("media: dvb-usb: az6027: fix null-ptr-deref in az6027_i2c_xfer()")

## References
- https://git.kernel.org/stable/c/1047f9343011f2cedc73c64829686206a7e9fc3f
- https://git.kernel.org/stable/c/5b1ea100ad3695025969dc4693f307877fb688d6
- https://git.kernel.org/stable/c/6ab7ea4e17d6a605d05308adf8f3408924770cba
- https://git.kernel.org/stable/c/991c77fe18c6f374bbf83376f8c42550aa565662
- https://git.kernel.org/stable/c/a1110f19d4940e4185251d072cbb0ff51486a1e7
- https://git.kernel.org/stable/c/a9def3e9718a4dc756f48db147d42ec41a966240
- https://git.kernel.org/stable/c/adcb73f8ce9aec48b1f85223f401c1574015d8d2
- https://git.kernel.org/stable/c/c6763fefa267f6e62595a6ac1f57815d99fc90b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53220.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53220
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

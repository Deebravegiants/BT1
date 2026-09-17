# [H] scsi: ses: Fix slab-out-of-bounds in ses_enclosure_data_process()

## Summary
Severity: High
Advisory: CVE-2023-53803
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53803
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ses: Fix slab-out-of-bounds in ses_enclosure_data_process()

A fix for:

BUG: KASAN: slab-out-of-bounds in ses_enclosure_data_process+0x949/0xe30 [ses]
Read of size 1 at addr ffff88a1b043a451 by task systemd-udevd/3271

Checking after (and before in next loop) addl_desc_ptr[1] is sufficient, we
expect the size to be sanitized before first access to addl_desc_ptr[1].
Make sure we don't walk beyond end of page.

## References
- https://git.kernel.org/stable/c/0dfe68394cbe1d4fe579fb325ecc813c50528c5a
- https://git.kernel.org/stable/c/2b28a7d261cb309912596d6a2d383ca370483527
- https://git.kernel.org/stable/c/467afb1dd630d8c6d172bd6cacc125199b5f4f2d
- https://git.kernel.org/stable/c/799e8dd2022d2e13f0c5c1906b40ceca07a23349
- https://git.kernel.org/stable/c/9b4f5028e493cb353a5c8f5c45073eeea0303abd
- https://git.kernel.org/stable/c/9e5c7d52085b8c84bc82a261580f0eb170039325
- https://git.kernel.org/stable/c/da1a955c48a16e16e925d6544793914e52a6fa51
- https://git.kernel.org/stable/c/e4dd25da784b2e07dbfbf04509afa4c5a1375227
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53803.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53803
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

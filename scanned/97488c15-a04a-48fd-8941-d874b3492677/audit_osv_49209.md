# [H] CVE-2018-5873

## Summary
Severity: High
Advisory: CVE-2018-5873
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2018-5873
Type: osv

## Details
An issue was discovered in the __ns_get_path function in fs/nsfs.c in the Linux kernel before 4.11. Due to a race condition when accessing files, a Use After Free condition can occur. This also affects all Android releases from CAF using the Linux kernel (Android for MSM, Firefox OS for MSM, QRD Android) before security patch level 2018-07-05.

## References
- https://source.android.com/security/bulletin/2018-07-01
- https://source.codeaurora.org/quic/la/kernel/msm-4.9/commit/?id=34742aaf7cb16c95edba4a7afed6d2c4fa7e434b
- https://www.codeaurora.org/security-bulletin/2018/07/02/july-2018-code-aurora-security-bulletin
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=073c516ff73557a8f7315066856c04b50383ac34
- https://github.com/torvalds/linux/commit/073c516ff73557a8f7315066856c04b50383ac34

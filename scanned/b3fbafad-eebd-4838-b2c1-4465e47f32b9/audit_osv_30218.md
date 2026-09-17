# [H] posix-clock: Fix missing timespec64 check in pc_clock_settime()

## Summary
Severity: High
Advisory: CVE-2024-50195
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50195
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

posix-clock: Fix missing timespec64 check in pc_clock_settime()

As Andrew pointed out, it will make sense that the PTP core
checked timespec64 struct's tv_sec and tv_nsec range before calling
ptp->info->settime64().

As the man manual of clock_settime() said, if tp.tv_sec is negative or
tp.tv_nsec is outside the range [0..999,999,999], it should return EINVAL,
which include dynamic clocks which handles PTP clock, and the condition is
consistent with timespec64_valid(). As Thomas suggested, timespec64_valid()
only check the timespec is valid, but not ensure that the time is
in a valid range, so check it ahead using timespec64_valid_strict()
in pc_clock_settime() and return -EINVAL if not valid.

There are some drivers that use tp->tv_sec and tp->tv_nsec directly to
write registers without validity checks and assume that the higher layer
has checked it, which is dangerous and will benefit from this, such as
hclge_ptp_settime(), igb_ptp_settime_i210(), _rcar_gen4_ptp_settime(),
and some drivers can remove the checks of itself.

## References
- https://git.kernel.org/stable/c/1ff7247101af723731ea42ed565d54fb8f341264
- https://git.kernel.org/stable/c/27abbde44b6e71ee3891de13e1a228aa7ce95bfe
- https://git.kernel.org/stable/c/29f085345cde24566efb751f39e5d367c381c584
- https://git.kernel.org/stable/c/673a1c5a2998acbd429d6286e6cad10f17f4f073
- https://git.kernel.org/stable/c/a3f169e398215e71361774d13bf91a0101283ac2
- https://git.kernel.org/stable/c/c8789fbe2bbf75845e45302cba6ffa44e1884d01
- https://git.kernel.org/stable/c/d8794ac20a299b647ba9958f6d657051fc51a540
- https://git.kernel.org/stable/c/e0c966bd3e31911b57ef76cec4c5796ebd88e512
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50195.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50195
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

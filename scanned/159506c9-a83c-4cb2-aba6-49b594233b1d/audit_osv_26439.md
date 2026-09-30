# [H] f2fs: fix to avoid potential memory corruption in __update_iostat_latency()

## Summary
Severity: High
Advisory: CVE-2023-53214
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53214
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid potential memory corruption in __update_iostat_latency()

Add iotype sanity check to avoid potential memory corruption.
This is to fix the compile error below:

fs/f2fs/iostat.c:231 __update_iostat_latency() error: buffer overflow
'io_lat->peak_lat[type]' 3 <= 3

vim +228 fs/f2fs/iostat.c

  211  static inline void __update_iostat_latency(struct bio_iostat_ctx
	*iostat_ctx,
  212					enum iostat_lat_type type)
  213  {
  214		unsigned long ts_diff;
  215		unsigned int page_type = iostat_ctx->type;
  216		struct f2fs_sb_info *sbi = iostat_ctx->sbi;
  217		struct iostat_lat_info *io_lat = sbi->iostat_io_lat;
  218		unsigned long flags;
  219
  220		if (!sbi->iostat_enable)
  221			return;
  222
  223		ts_diff = jiffies - iostat_ctx->submit_ts;
  224		if (page_type >= META_FLUSH)
                                 ^^^^^^^^^^

  225			page_type = META;
  226
  227		spin_lock_irqsave(&sbi->iostat_lat_lock, flags);
 @228		io_lat->sum_lat[type][page_type] += ts_diff;
                                      ^^^^^^^^^
Mixup between META_FLUSH and NR_PAGE_TYPE leads to memory corruption.

## References
- https://git.kernel.org/stable/c/0dbbf0fb38d5ec5d4138d1aeaeb43d9217b9a592
- https://git.kernel.org/stable/c/20b4f3de0f3932f71b4a8daf0671e517a8d98022
- https://git.kernel.org/stable/c/22ddbbff116ee7dce5431feb1c0f36a507d2d68d
- https://git.kernel.org/stable/c/aa4d726af72a21732ce120484e0b1240674a13b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53214.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53214
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

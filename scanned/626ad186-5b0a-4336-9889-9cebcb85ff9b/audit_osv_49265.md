# [M] CVE-2018-7754

## Summary
Severity: Medium
Advisory: CVE-2018-7754
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-10
Source: https://osv.dev/vulnerability/CVE-2018-7754
Type: osv

## Details
The aoedisk_debugfs_show function in drivers/block/aoe/aoeblk.c in the Linux kernel through 4.16.4rc4 allows local users to obtain sensitive address information by reading "ffree: " lines in a debugfs file.

## References
- https://elixir.bootlin.com/linux/v4.16-rc4/source/drivers/block/aoe/aoeblk.c#L421
- https://github.com/johnsonwangqize/cve-linux/blob/master/CVE-2018-7754.md

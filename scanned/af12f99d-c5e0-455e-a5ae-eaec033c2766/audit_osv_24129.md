# [H] ext4: fix potential out of bound read in ext4_fc_replay_scan()

## Summary
Severity: High
Advisory: CVE-2022-50306
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50306
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.87, >=5.16.0 <6.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix potential out of bound read in ext4_fc_replay_scan()

For scan loop must ensure that at least EXT4_FC_TAG_BASE_LEN space. If remain
space less than EXT4_FC_TAG_BASE_LEN which will lead to out of bound read
when mounting corrupt file system image.
ADD_RANGE/HEAD/TAIL is needed to add extra check when do journal scan, as this
three tags will read data during scan, tag length couldn't less than data length
which will read.

## References
- https://git.kernel.org/stable/c/1b45cc5c7b920fd8bf72e5a888ec7abeadf41e09
- https://git.kernel.org/stable/c/6969367c1500c15eddc38fda12f6d15518ad6d03
- https://git.kernel.org/stable/c/f234294812c9b68d603650d28743eafb718e7ad5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50306.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

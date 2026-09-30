# [H] udf: fix uninit-value use in udf_get_fileshortad

## Summary
Severity: High
Advisory: CVE-2024-50143
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50143
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.246, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: fix uninit-value use in udf_get_fileshortad

Check for overflow when computing alen in udf_current_aext to mitigate
later uninit-value use in udf_get_fileshortad KMSAN bug[1].
After applying the patch reproducer did not trigger any issue[2].

[1] https://syzkaller.appspot.com/bug?extid=8901c4560b7ab5c2f9df
[2] https://syzkaller.appspot.com/x/log.txt?x=10242227980000

## References
- https://git.kernel.org/stable/c/0ce61b1f6b32df822b59c680cbe8e5ba5d335742
- https://git.kernel.org/stable/c/1ac49babc952f48d82676979b20885e480e69be8
- https://git.kernel.org/stable/c/264db9d666ad9a35075cc9ed9ec09d021580fbb1
- https://git.kernel.org/stable/c/417bd613bdbe791549f7687bb1b9b8012ff111c2
- https://git.kernel.org/stable/c/4fc0d8660e391dcd8dde23c44d702be1f6846c61
- https://git.kernel.org/stable/c/5eb76fb98b3335aa5cca6a7db2e659561c79c32b
- https://git.kernel.org/stable/c/72e445df65a0aa9066c6fe2b8736ba2fcca6dac7
- https://git.kernel.org/stable/c/e52e0b92ed31dc62afbda15c243dcee0bb5bb58d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50143.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50143
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

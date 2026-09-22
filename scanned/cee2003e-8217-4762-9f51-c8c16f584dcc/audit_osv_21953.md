# [M] CVE-2022-1678

## Summary
Severity: Medium
Advisory: CVE-2022-1678
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-25
Source: https://osv.dev/vulnerability/CVE-2022-1678
Type: osv

## Details
An issue was discovered in the Linux Kernel from 4.18 to 4.19, an improper update of sock reference in TCP pacing can lead to memory/netns leak, which can be used by remote clients.

## References
- https://anas.openanolis.cn/cves/detail/CVE-2022-1678
- https://anas.openanolis.cn/errata/detail/ANSA-2022:0143
- https://gitee.com/anolis/cloud-kernel/commit/bed537da691b
- https://lore.kernel.org/all/20200602080425.93712-1-kerneljasonxing%40gmail.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1678.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1678
- https://security.netapp.com/advisory/ntap-20220715-0001/
- https://bugzilla.openanolis.cn/show_bug.cgi?id=61
- https://github.com/torvalds/linux/commit/0a70f118475e037732557796accd0878a00fc25a

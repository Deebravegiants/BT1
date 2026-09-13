# [H] dm-integrity: don't increment hash_offset twice

## Summary
Severity: High
Advisory: CVE-2026-72099
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72099
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-integrity: don't increment hash_offset twice

hash_offset is already incremented in the loop "for (i = 0; i < to_copy;
i++, ts--)". Do not increment it again.

## References
- https://git.kernel.org/stable/c/39697e2759ac23e65361fe61482f8174cad8a752
- https://git.kernel.org/stable/c/4f4e43337e9ef322595201cfc24def50fd624219
- https://git.kernel.org/stable/c/5dfd8042635278613da3b88553e25ade2103cd58
- https://git.kernel.org/stable/c/829476c06496aab018f14127c055adb164d1a750
- https://git.kernel.org/stable/c/c66b1781a54984227e94b862be9328d81d81e51c
- https://git.kernel.org/stable/c/cf9feed8c131e303ecf2afebe6f791be018818ad
- https://git.kernel.org/stable/c/e6646f4d711d74930d39cce6fb7bfcae4cbee5fd
- https://git.kernel.org/stable/c/edf025f083854f80032b73a1aad69a3c90db236f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

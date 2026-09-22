# [M] staging: iio: frequency: ad9832: fix division by zero in ad9832_calc_freqreg()

## Summary
Severity: Medium
Advisory: CVE-2024-50233
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50233
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: iio: frequency: ad9832: fix division by zero in ad9832_calc_freqreg()

In the ad9832_write_frequency() function, clk_get_rate() might return 0.
This can lead to a division by zero when calling ad9832_calc_freqreg().
The check if (fout > (clk_get_rate(st->mclk) / 2)) does not protect
against the case when fout is 0. The ad9832_write_frequency() function
is called from ad9832_write(), and fout is derived from a text buffer,
which can contain any value.

## References
- https://git.kernel.org/stable/c/2f39548f45693d86e950647012a214da6917dc9f
- https://git.kernel.org/stable/c/442f786c5bff8cfd756ebdeaa4aadbf05c22aa5a
- https://git.kernel.org/stable/c/6bd301819f8f69331a55ae2336c8b111fc933f3d
- https://git.kernel.org/stable/c/adfbc08b94e7df08b9ed5fa26b969cc1b54c84ec
- https://git.kernel.org/stable/c/ccbc10647aafe2b7506edb4b10e19c6c2416c162
- https://git.kernel.org/stable/c/dd9e1cf619c945f320e686dcaf13e37ef0b05fdd
- https://git.kernel.org/stable/c/fcd6b59f7a774558e2525251c68aa37aff748e55
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50233.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

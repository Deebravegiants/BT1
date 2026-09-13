# [M] iio: magnetometer: rm3100: add boundary check for the value read from RM3100_REG_TMRC

## Summary
Severity: Medium
Advisory: CVE-2024-26702
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26702
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: magnetometer: rm3100: add boundary check for the value read from RM3100_REG_TMRC

Recently, we encounter kernel crash in function rm3100_common_probe
caused by out of bound access of array rm3100_samp_rates (because of
underlying hardware failures). Add boundary check to prevent out of
bound access.

## References
- https://git.kernel.org/stable/c/176256ff8abff29335ecff905a09fb49e8dcf513
- https://git.kernel.org/stable/c/1d8c67e94e9e977603473a543d4f322cf2c4aa01
- https://git.kernel.org/stable/c/36a49290d7e6d554020057a409747a092b1d3b56
- https://git.kernel.org/stable/c/57d05dbbcd0b3dc0c252103b43012eef5d6430d1
- https://git.kernel.org/stable/c/7200170e88e3ec54d9e9c63f07514c3cead11481
- https://git.kernel.org/stable/c/792595bab4925aa06532a14dd256db523eb4fa5e
- https://git.kernel.org/stable/c/8d5838a473e8e6d812257c69745f5920e4924a60
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26702.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26702
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

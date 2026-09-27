# [M] rtc: pl031: fix rtc features null pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2022-49273
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49273
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtc: pl031: fix rtc features null pointer dereference

When there is no interrupt line, rtc alarm feature is disabled.

The clearing of the alarm feature bit was being done prior to allocations
of ldata->rtc device, resulting in a null pointer dereference.

Clear RTC_FEATURE_ALARM after the rtc device is allocated.

## References
- https://git.kernel.org/stable/c/1b915703964f7e636961df04c540261dc55c6c70
- https://git.kernel.org/stable/c/cd2722e411e8ab7e5ae41102f6925fa13dffdac5
- https://git.kernel.org/stable/c/d274ce4a3dfd0b9a292667535578359b865765cb
- https://git.kernel.org/stable/c/ea6af39f3da50c86367a71eb3cc674ade3ed244c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49273.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

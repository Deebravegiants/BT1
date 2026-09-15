# [M] gpio: gpio-xilinx: Fix integer overflow

## Summary
Severity: Medium
Advisory: CVE-2022-49570
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49570
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: gpio-xilinx: Fix integer overflow

Current implementation is not able to configure more than 32 pins
due to incorrect data type. So type casting with unsigned long
to avoid it.

## References
- https://git.kernel.org/stable/c/32c094a09d5829ad9b02cdf667569aefa8de0ea6
- https://git.kernel.org/stable/c/6f16a5390640807dde420ee5ccbc4c95577aea6a
- https://git.kernel.org/stable/c/e129e5486b981d324057e6986059f852658b0d00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49570.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

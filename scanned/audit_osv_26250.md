# [M] iio: adc: ad7091r: Allow users to configure device events

## Summary
Severity: Medium
Advisory: CVE-2023-52627
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2023-52627
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad7091r: Allow users to configure device events

AD7091R-5 devices are supported by the ad7091r-5 driver together with
the ad7091r-base driver. Those drivers declared iio events for notifying
user space when ADC readings fall bellow the thresholds of low limit
registers or above the values set in high limit registers.
However, to configure iio events and their thresholds, a set of callback
functions must be implemented and those were not present until now.
The consequence of trying to configure ad7091r-5 events without the
proper callback functions was a null pointer dereference in the kernel
because the pointers to the callback functions were not set.

Implement event configuration callbacks allowing users to read/write
event thresholds and enable/disable event generation.

Since the event spec structs are generic to AD7091R devices, also move
those from the ad7091r-5 driver the base driver so they can be reused
when support for ad7091r-2/-4/-8 be added.

## References
- https://git.kernel.org/stable/c/020e71c7ffc25dfe29ed9be6c2d39af7bd7f661f
- https://git.kernel.org/stable/c/137568aa540a9f587c48ff7d4c51cdba08cfe9a4
- https://git.kernel.org/stable/c/1eba6f7ffa295a0eec098c107043074be7cc4ec5
- https://git.kernel.org/stable/c/49f322ce1f265935f15e5512da69a399f27a5091
- https://git.kernel.org/stable/c/55aca2ce91a63740278502066beaddbd841af9c6
- https://git.kernel.org/stable/c/89c4e63324e208a23098f7fb15c00487cecbfed2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52627.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

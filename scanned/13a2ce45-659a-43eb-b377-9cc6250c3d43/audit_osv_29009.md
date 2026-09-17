# [M] ALSA: timer: Set lower bound of start tick time

## Summary
Severity: Medium
Advisory: CVE-2024-38618
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38618
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: timer: Set lower bound of start tick time

Currently ALSA timer doesn't have the lower limit of the start tick
time, and it allows a very small size, e.g. 1 tick with 1ns resolution
for hrtimer.  Such a situation may lead to an unexpected RCU stall,
where  the callback repeatedly queuing the expire update, as reported
by fuzzer.

This patch introduces a sanity check of the timer start tick time, so
that the system returns an error when a too small start size is set.
As of this patch, the lower limit is hard-coded to 100us, which is
small enough but can still work somehow.

## References
- https://git.kernel.org/stable/c/2c95241ac5fc90c929d6c0c023e84bf0d30e84c3
- https://git.kernel.org/stable/c/4a63bd179fa8d3fcc44a0d9d71d941ddd62f0c4e
- https://git.kernel.org/stable/c/68396c825c43664b20a3a1ba546844deb2b4e48f
- https://git.kernel.org/stable/c/74bfb8d90f2601718ae203faf45a196844c01fa1
- https://git.kernel.org/stable/c/83f0ba8592b9e258fd80ac6486510ab1dcd7ad6e
- https://git.kernel.org/stable/c/abb1ad69d98cf1ff25bb14fff0e7c3f66239e1cd
- https://git.kernel.org/stable/c/bdd0aa055b8ec7e24bbc19513f3231958741d0ab
- https://git.kernel.org/stable/c/ceab795a67dd28dd942d0d8bba648c6c0f7a044b
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38618.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38618
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

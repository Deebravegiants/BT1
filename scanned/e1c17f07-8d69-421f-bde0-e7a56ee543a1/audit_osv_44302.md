# [H] Input: synaptics-rmi4 - fix F55 transmitter electrode count typo

## Summary
Severity: High
Advisory: CVE-2026-80754
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80754
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: synaptics-rmi4 - fix F55 transmitter electrode count typo

During F55 sensor detection, the transmitter (TX) electrode count was
incorrectly assigned the value of the receiver (RX) electrode count
due to copy-paste typos.

This incorrect value was then propagated to the driver data and used
by F54 to determine the diagnostics report size. On devices with more
RX than TX electrodes, this inflated the perceived TX count, leading
to incorrect report size calculations and potential out-of-bounds
buffer accesses.

Fix the typos by correctly assigning the TX electrode counts.

## References
- https://git.kernel.org/stable/c/0739c65e799d4a93fe573ed23255a71fcfcc5438
- https://git.kernel.org/stable/c/6058f0fea10f3caf63a435677358d1b8e9325114
- https://git.kernel.org/stable/c/6484e00d6778fdf2209cd75940bc3902b276457f
- https://git.kernel.org/stable/c/9759502f5cd71805923457f183ae5b9533e20c7b
- https://git.kernel.org/stable/c/9b184c8337c6e12df129399007735a7fbcbbcb7b
- https://git.kernel.org/stable/c/a6d9646e77da7cab2dff7043a8e9f75e23b836bc
- https://git.kernel.org/stable/c/a81cafe3c3c2f8494063385a7b0ea7ff407bf19f
- https://git.kernel.org/stable/c/db4e20265ebda729610ca5cf45ca9437462c3f36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80754.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80754
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

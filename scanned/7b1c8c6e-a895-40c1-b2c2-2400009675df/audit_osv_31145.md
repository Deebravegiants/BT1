# [H] rtc: pcf85063: fix potential OOB write in PCF85063 NVMEM read

## Summary
Severity: High
Advisory: CVE-2024-58069
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58069
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtc: pcf85063: fix potential OOB write in PCF85063 NVMEM read

The nvmem interface supports variable buffer sizes, while the regmap
interface operates with fixed-size storage. If an nvmem client uses a
buffer size less than 4 bytes, regmap_read will write out of bounds
as it expects the buffer to point at an unsigned int.

Fix this by using an intermediary unsigned int to hold the value.

## References
- https://git.kernel.org/stable/c/21cd59fcb9952eb7505da2bdfc1eb9c619df3ff4
- https://git.kernel.org/stable/c/3ab8c5ed4f84fa20cd16794fe8dc31f633fbc70c
- https://git.kernel.org/stable/c/517aedb365f2c94e2d7e0b908ac7127df76203a1
- https://git.kernel.org/stable/c/6f2a8ca9a0a38589f52a7f0fb9425b9ba987ae7c
- https://git.kernel.org/stable/c/9adefa7b9559d0f21034a5d5ec1b55840c9348b9
- https://git.kernel.org/stable/c/c72b7a474d3f445bf0c5bcf8ffed332c78eb28a1
- https://git.kernel.org/stable/c/e5536677da803ed54a29a446515c28dce7d3d574
- https://git.kernel.org/stable/c/e5e06455760f2995b16a176033909347929d1128
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] thermal: core: Free tzp copy along with the thermal zone

## Summary
Severity: High
Advisory: CVE-2024-50027
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50027
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.60, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: core: Free tzp copy along with the thermal zone

The object pointed to by tz->tzp may still be accessed after being
freed in thermal_zone_device_unregister(), so move the freeing of it
to the point after the removal completion has been completed at which
it cannot be accessed any more.

## References
- https://git.kernel.org/stable/c/827a07525c099f54d3b15110408824541ec66b3c
- https://git.kernel.org/stable/c/bdb0d40507c85bee33c2a71fde7b2e857346f112
- https://git.kernel.org/stable/c/eabe285e1c629a719d6e68fc319939c63b83bf22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50027.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

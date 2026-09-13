# [M] CVE-2023-2194

## Summary
Severity: Medium
Advisory: CVE-2023-2194
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2023-2194
Type: osv

## Details
An out-of-bounds write vulnerability was found in the Linux kernel's SLIMpro I2C device driver. The userspace "data->block[0]" variable was not capped to a number between 0-255 and was used as the size of a memcpy, possibly writing beyond the end of dma_buffer. This flaw could allow a local privileged user to crash the system or potentially achieve code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2194.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2194
- https://bugzilla.redhat.com/show_bug.cgi?id=2188396
- https://github.com/torvalds/linux/commit/92fbb6d1296f
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html

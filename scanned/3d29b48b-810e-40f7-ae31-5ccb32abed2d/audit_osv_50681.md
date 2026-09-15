# [M] CVE-2020-27835

## Summary
Severity: Medium
Advisory: CVE-2020-27835
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-27835
Type: osv

## Details
A use after free in the Linux kernel infiniband hfi1 driver in versions prior to 5.10-rc6 was found in the way user calls Ioctl after open dev file and fork. A local user could use this flaw to crash the system.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1901709

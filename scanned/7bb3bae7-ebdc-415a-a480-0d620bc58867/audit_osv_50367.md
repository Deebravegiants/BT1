# [M] CVE-2020-14304

## Summary
Severity: Medium
Advisory: CVE-2020-14304
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-14304
Type: osv

## Details
A memory disclosure flaw was found in the Linux kernel's ethernet drivers, in the way it read data from the EEPROM of the device. This flaw allows a local user to read uninitialized values from the kernel memory. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=960702
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14304

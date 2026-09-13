# [M] scsi: ibmvfc: Remove BUG_ON in the case of an empty event pool

## Summary
Severity: Medium
Advisory: CVE-2023-52811
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52811
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ibmvfc: Remove BUG_ON in the case of an empty event pool

In practice the driver should never send more commands than are allocated
to a queue's event pool. In the unlikely event that this happens, the code
asserts a BUG_ON, and in the case that the kernel is not configured to
crash on panic returns a junk event pointer from the empty event list
causing things to spiral from there. This BUG_ON is a historical artifact
of the ibmvfc driver first being upstreamed, and it is well known now that
the use of BUG_ON is bad practice except in the most unrecoverable
scenario. There is nothing about this scenario that prevents the driver
from recovering and carrying on.

Remove the BUG_ON in question from ibmvfc_get_event() and return a NULL
pointer in the case of an empty event pool. Update all call sites to
ibmvfc_get_event() to check for a NULL pointer and perfrom the appropriate
failure or recovery action.

## References
- https://git.kernel.org/stable/c/88984ec4792766df5a9de7a2ff2b5f281f94c7d4
- https://git.kernel.org/stable/c/8bbe784c2ff28d56ca0c548aaf3e584edc77052d
- https://git.kernel.org/stable/c/b39f2d10b86d0af353ea339e5815820026bca48f
- https://git.kernel.org/stable/c/d2af4ef80601224b90630c1ddc7cd2c7c8ab4dd8
- https://git.kernel.org/stable/c/e1d1f79b1929dce470a5dc9281c574cd58e8c6c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52811.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52811
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] CVE-2017-18549

## Summary
Severity: Medium
Advisory: CVE-2017-18549
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2017-18549
Type: osv

## Details
An issue was discovered in drivers/scsi/aacraid/commctrl.c in the Linux kernel before 4.13. There is potential exposure of kernel stack memory because aac_send_raw_srb does not initialize the reply structure.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=342ffc26693b528648bdc9377e51e4f2450b4860

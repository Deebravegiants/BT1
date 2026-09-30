# [H] CVE-2021-26930

## Summary
Severity: High
Advisory: CVE-2021-26930
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2021-26930
Type: osv

## Details
An issue was discovered in the Linux kernel 3.11 through 5.10.16, as used by Xen. To service requests to the PV backend, the driver maps grant references provided by the frontend. In this process, errors may be encountered. In one case, an error encountered earlier might be discarded by later processing, resulting in the caller assuming successful mapping, and hence subsequent operations trying to access space that wasn't mapped. In another case, internal state would be insufficiently updated, preventing safe recovery from the error. This affects drivers/block/xen-blkback/blkback.c.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=871997bc9e423f05c7da7c9178e62dde5df2a7f8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2XQR52ICKRK3GC4HDWLMWF2U55YGAR63/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GWQWPWYZRXVFJI5M3VCM72X27IB7CKOB/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://security.netapp.com/advisory/ntap-20210326-0001/
- http://xenbits.xen.org/xsa/advisory-365.html

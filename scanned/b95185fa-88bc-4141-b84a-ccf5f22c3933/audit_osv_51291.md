# [H] CVE-2021-26934

## Summary
Severity: High
Advisory: CVE-2021-26934
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2021-26934
Type: osv

## Details
An issue was discovered in the Linux kernel 4.18 through 5.10.16, as used by Xen. The backend allocation (aka be-alloc) mode of the drm_xen_front drivers was not meant to be a supported configuration, but this wasn't stated accordingly in its support status entry.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4GELN5E6MDR5KQBJF5M5COUUED3YFZTD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EOAJBVAVR6RSCUCHNXPVSNRPSFM7INMP/
- https://security.netapp.com/advisory/ntap-20210326-0001/
- http://xenbits.xen.org/xsa/advisory-363.html

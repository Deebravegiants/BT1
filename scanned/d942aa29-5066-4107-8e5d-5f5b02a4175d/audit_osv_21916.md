# [H] CVE-2022-1304

## Summary
Severity: High
Advisory: CVE-2022-1304
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-14
Source: https://osv.dev/vulnerability/CVE-2022-1304
Type: osv

## Details
An out-of-bounds read/write vulnerability was found in e2fsprogs 1.46.5. This issue leads to a segmentation fault and possibly arbitrary code execution via a specially crafted filesystem.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1304.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1304
- https://security.netapp.com/advisory/ntap-20241122-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=2069726

# [M] CVE-2018-6616

## Summary
Severity: Medium
Advisory: CVE-2018-6616
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-04
Source: https://osv.dev/vulnerability/CVE-2018-6616
Type: osv

## Details
In OpenJPEG 2.3.0, there is excessive iteration in the opj_t1_encode_cblks function of openjp2/t1.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file.

## References
- https://lists.debian.org/debian-lts-announce/2018/12/msg00013.html
- https://usn.ubuntu.com/4109-1/
- https://www.debian.org/security/2019/dsa-4405
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://github.com/uclouvain/openjpeg/issues/1059

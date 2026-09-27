# [M] CVE-2018-5785

## Summary
Severity: Medium
Advisory: CVE-2018-5785
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-19
Source: https://osv.dev/vulnerability/CVE-2018-5785
Type: osv

## Details
In OpenJPEG 2.3.0, there is an integer overflow caused by an out-of-bounds left shift in the opj_j2k_setup_encoder function (openjp2/j2k.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file.

## References
- https://usn.ubuntu.com/4109-1/
- https://www.debian.org/security/2019/dsa-4405
- https://github.com/uclouvain/openjpeg/issues/1057

# [M] CVE-2018-5727

## Summary
Severity: Medium
Advisory: CVE-2018-5727
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5727
Type: osv

## Details
In OpenJPEG 2.3.0, there is an integer overflow vulnerability in the opj_t1_encode_cblks function (openjp2/t1.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file.

## References
- https://github.com/uclouvain/openjpeg/issues/1053

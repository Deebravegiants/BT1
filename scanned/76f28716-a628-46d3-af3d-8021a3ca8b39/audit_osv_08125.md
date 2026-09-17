# [M] CVE-2016-10504

## Summary
Severity: Medium
Advisory: CVE-2016-10504
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2016-10504
Type: osv

## Details
Heap-based buffer overflow vulnerability in the opj_mqc_byteout function in mqc.c in OpenJPEG before 2.2.0 allows remote attackers to cause a denial of service (application crash) via a crafted bmp file.

## References
- http://www.securityfocus.com/bid/100564
- https://www.exploit-db.com/exploits/42600/
- http://www.debian.org/security/2017/dsa-4013
- https://security.gentoo.org/glsa/201710-26
- https://github.com/uclouvain/openjpeg/commit/397f62c0a838e15d667ef50e27d5d011d2c79c04
- https://github.com/uclouvain/openjpeg/issues/835

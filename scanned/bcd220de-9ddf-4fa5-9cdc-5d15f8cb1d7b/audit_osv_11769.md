# [H] CVE-2017-9614

## Summary
Severity: High
Advisory: CVE-2017-9614
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-9614
Type: osv

## Details
The fill_input_buffer function in jdatasrc.c in libjpeg-turbo 1.5.1 allows remote attackers to cause a denial of service (invalid memory access and application crash) or possibly have unspecified other impact via a crafted jpg file. NOTE: Maintainer asserts the issue is due to a bug in downstream code caused by misuse of the libjpeg API

## References
- http://packetstormsecurity.com/files/143518/libjpeg-turbo-1.5.1-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2017/Jul/66
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/167
- https://www.exploit-db.com/exploits/42391/

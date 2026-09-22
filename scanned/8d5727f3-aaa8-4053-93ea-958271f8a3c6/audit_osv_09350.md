# [M] CVE-2016-9561

## Summary
Severity: Medium
Advisory: CVE-2016-9561
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9561
Type: osv

## Details
The che_configure function in libavcodec/aacdec_template.c in FFmpeg before 3.2.1 allows remote attackers to cause a denial of service (allocation of huge memory, and being killed by the OS) via a crafted MOV file.

## References
- http://www.securityfocus.com/bid/94756
- http://www.openwall.com/lists/oss-security/2016/12/08/1

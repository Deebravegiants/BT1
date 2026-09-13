# [M] CVE-2016-10172

## Summary
Severity: Medium
Advisory: CVE-2016-10172
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2016-10172
Type: osv

## Details
The read_new_config_info function in open_utils.c in Wavpack before 5.1.0 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted WV file.

## References
- http://www.securityfocus.com/bid/95883
- http://www.openwall.com/lists/oss-security/2017/01/28/9
- https://github.com/dbry/WavPack/commit/4bc05fc490b66ef2d45b1de26abf1455b486b0dc
- https://sourceforge.net/p/wavpack/mailman/message/35561951/

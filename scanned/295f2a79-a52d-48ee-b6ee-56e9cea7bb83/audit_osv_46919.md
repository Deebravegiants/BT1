# [H] CVE-2015-8026

## Summary
Severity: High
Advisory: CVE-2015-8026
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2015-8026
Type: osv

## Details
Heap-based buffer overflow in the verify_vbr_checksum function in exfatfsck in exfat-utils before 1.2.1 allows remote attackers to cause a denial of service (infinite loop) or possibly execute arbitrary code via a crafted filesystem.

## References
- http://www.openwall.com/lists/oss-security/2015/10/29/13
- http://www.securityfocus.com/bid/77307
- https://blog.fuzzing-project.org/25-Heap-overflow-and-endless-loop-in-exfatfsck-exfat-utils.html
- https://github.com/relan/exfat/commit/2e86ae5f81da11f11673d0546efb525af02b7786
- https://github.com/relan/exfat/issues/5
- https://security.gentoo.org/glsa/201612-31
- http://www.openwall.com/lists/oss-security/2015/10/29/13
- http://www.openwall.com/lists/oss-security/2015/10/29/13
- https://github.com/relan/exfat/commit/2e86ae5f81da11f11673d0546efb525af02b7786
- https://github.com/relan/exfat/issues/5
- https://security.gentoo.org/glsa/201612-31
- https://github.com/relan/exfat/commit/2e86ae5f81da11f11673d0546efb525af02b7786
- https://github.com/relan/exfat/issues/5

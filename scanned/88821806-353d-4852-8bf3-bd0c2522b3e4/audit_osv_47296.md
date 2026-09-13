# [H] CVE-2016-2335

## Summary
Severity: High
Advisory: CVE-2016-2335
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2016-2335
Type: osv

## Details
The CInArchive::ReadFileItem method in Archive/Udf/UdfIn.cpp in 7zip 9.20 and 15.05 beta and p7zip allows remote attackers to cause a denial of service (out-of-bounds read) or execute arbitrary code via the PartitionRef field in the Long Allocation Descriptor in a UDF file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DNYIQAU3FKFBNFPK6GKYTSVRHQA7PTYT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DTGWICT3KYYDPDXRNO5SXD32GZICGRIR/
- https://usn.ubuntu.com/3913-1/
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00004.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00098.html
- http://www.securitytracker.com/id/1035876
- https://security.gentoo.org/glsa/201701-27
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00069.html
- http://www.debian.org/security/2016/dsa-3599
- http://www.oracle.com/technetwork/topics/security/bulletinoct2016-3090566.html
- http://www.securityfocus.com/bid/90531
- http://blog.talosintel.com/2016/05/multiple-7-zip-vulnerabilities.html
- http://www.talosintel.com/reports/TALOS-2016-0094/

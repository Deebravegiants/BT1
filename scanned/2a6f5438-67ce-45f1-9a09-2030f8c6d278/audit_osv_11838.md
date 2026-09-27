# [M] CVE-2018-0202

## Summary
Severity: Medium
Advisory: CVE-2018-0202
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-0202
Type: osv

## Details
clamscan in ClamAV before 0.99.4 contains a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to improper input validation checking mechanisms when handling Portable Document Format (.pdf) files sent to an affected device. An unauthenticated, remote attacker could exploit this vulnerability by sending a crafted .pdf file to an affected device. This action could cause an out-of-bounds read when ClamAV scans the malicious file, allowing the attacker to cause a DoS condition. This concerns pdf_parse_array and pdf_parse_string in libclamav/pdfng.c. Cisco Bug IDs: CSCvh91380, CSCvh91400.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00011.html
- https://security.gentoo.org/glsa/201804-16
- https://usn.ubuntu.com/3592-1/
- https://usn.ubuntu.com/3592-2/
- https://bugzilla.clamav.net/show_bug.cgi?id=11980
- https://bugzilla.clamav.net/show_bug.cgi?id=11973

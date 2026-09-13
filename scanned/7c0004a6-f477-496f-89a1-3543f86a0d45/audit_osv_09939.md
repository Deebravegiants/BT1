# [H] CVE-2017-12376

## Summary
Severity: High
Advisory: CVE-2017-12376
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-12376
Type: osv

## Details
ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition or potentially execute arbitrary code on an affected device. The vulnerability is due to improper input validation checking mechanisms when handling Portable Document Format (.pdf) files sent to an affected device. An unauthenticated, remote attacker could exploit this vulnerability by sending a crafted .pdf file to an affected device. This action could cause a handle_pdfname (in pdf.c) buffer overflow when ClamAV scans the malicious file, allowing the attacker to cause a DoS condition or potentially execute arbitrary code.

## References
- https://usn.ubuntu.com/3550-1/
- https://usn.ubuntu.com/3550-2/
- http://blog.clamav.net/2018/01/clamav-0993-has-been-released.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00035.html
- https://bugzilla.clamav.net/show_bug.cgi?id=11942

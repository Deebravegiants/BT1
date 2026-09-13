# [H] CVE-2017-12375

## Summary
Severity: High
Advisory: CVE-2017-12375
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-12375
Type: osv

## Details
The ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to a lack of input validation checking mechanisms during certain mail parsing functions (the rfc2047 function in mbox.c). An unauthenticated, remote attacker could exploit this vulnerability by sending a crafted email to the affected device. This action could cause a buffer overflow condition when ClamAV scans the malicious email, allowing the attacker to potentially cause a DoS condition on an affected device.

## References
- https://usn.ubuntu.com/3550-1/
- https://usn.ubuntu.com/3550-2/
- http://blog.clamav.net/2018/01/clamav-0993-has-been-released.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00035.html
- https://bugzilla.clamav.net/show_bug.cgi?id=11940

# [M] CVE-2017-12378

## Summary
Severity: Medium
Advisory: CVE-2017-12378
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-12378
Type: osv

## Details
ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to improper input validation checking mechanisms of .tar (Tape Archive) files sent to an affected device. A successful exploit could cause a checksum buffer over-read condition when ClamAV scans the malicious .tar file, potentially allowing the attacker to cause a DoS condition on the affected device.

## References
- https://usn.ubuntu.com/3550-1/
- https://usn.ubuntu.com/3550-2/
- http://blog.clamav.net/2018/01/clamav-0993-has-been-released.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00035.html
- https://bugzilla.clamav.net/show_bug.cgi?id=11946

# [H] CVE-2017-12374

## Summary
Severity: High
Advisory: CVE-2017-12374
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2017-12374
Type: osv

## Details
The ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to a lack of input validation checking mechanisms during certain mail parsing operations (mbox.c operations on bounce messages). If successfully exploited, the ClamAV software could allow a variable pointing to the mail body which could cause a used after being free (use-after-free) instance which may lead to a disruption of services on an affected device to include a denial of service condition.

## References
- https://usn.ubuntu.com/3550-1/
- https://usn.ubuntu.com/3550-2/
- http://blog.clamav.net/2018/01/clamav-0993-has-been-released.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00035.html
- https://bugzilla.clamav.net/show_bug.cgi?id=11939

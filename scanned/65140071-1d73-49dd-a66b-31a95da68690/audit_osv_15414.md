# [M] CVE-2019-15961

## Summary
Severity: Medium
Advisory: CVE-2019-15961
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-15
Source: https://osv.dev/vulnerability/CVE-2019-15961
Type: osv

## Details
A vulnerability in the email parsing module Clam AntiVirus (ClamAV) Software versions 0.102.0, 0.101.4 and prior could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to inefficient MIME parsing routines that result in extremely long scan times of specially formatted email files. An attacker could exploit this vulnerability by sending a crafted email file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process to scan the crafted email file indefinitely, resulting in a denial of service condition.

## References
- https://lists.debian.org/debian-lts-announce/2020/02/msg00016.html
- https://quickview.cloudapps.cisco.com/quickview/bug/CSCvr56010
- https://security.gentoo.org/glsa/202003-46
- https://usn.ubuntu.com/4230-2/
- https://bugzilla.clamav.net/show_bug.cgi?id=12380

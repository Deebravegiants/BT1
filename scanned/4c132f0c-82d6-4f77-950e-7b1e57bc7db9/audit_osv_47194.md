# [C] CVE-2016-10229

## Summary
Severity: Critical
Advisory: CVE-2016-10229
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/CVE-2016-10229
Type: osv

## Details
udp.c in the Linux kernel before 4.5 allows remote attackers to execute arbitrary code via UDP traffic that triggers an unsafe second checksum calculation during execution of a recv system call with the MSG_PEEK flag.

## References
- http://www.securityfocus.com/bid/97397
- http://www.securitytracker.com/id/1038201
- https://security.paloaltonetworks.com/CVE-2016-10229
- https://security.netapp.com/advisory/ntap-20250103-0008/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=197c949e7798fbf28cfadc69d9ca0c2abbf93191
- http://source.android.com/security/bulletin/2017-04-01.html
- https://github.com/torvalds/linux/commit/197c949e7798fbf28cfadc69d9ca0c2abbf93191

# [H] CVE-2018-16948

## Summary
Severity: High
Advisory: CVE-2018-16948
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-16948
Type: osv

## Details
An issue was discovered in OpenAFS before 1.6.23 and 1.8.x before 1.8.2. Several RPC server routines did not fully initialize their output variables before returning, leaking memory contents from both the stack and the heap. Because the OpenAFS cache manager functions as an Rx server for the AFSCB service, clients are also susceptible to information leakage. For example, RXAFSCB_TellMeAboutYourself leaks kernel memory and KAM_ListEntry leaks kaserver memory.

## References
- http://openafs.org/pages/security/OPENAFS-SA-2018-002.txt
- https://lists.debian.org/debian-lts-announce/2018/09/msg00024.html
- https://www.debian.org/security/2018/dsa-4302

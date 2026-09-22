# [C] CVE-2017-9103

## Summary
Severity: Critical
Advisory: CVE-2017-9103
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2017-9103
Type: osv

## Details
An issue was discovered in adns before 1.5.2. pap_mailbox822 does not properly check st from adns__findlabel_next. Without this, an uninitialised stack value can be used as the first label length. Depending on the circumstances, an attacker might be able to trick adns into crashing the calling program, leaking aspects of the contents of some of its memory, causing it to allocate lots of memory, or perhaps overrunning a buffer. This is only possible with applications which make non-raw queries for SOA or RP records.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGFZ4SPV6KFQK6ZNUZFB5Y32OYFOM5YJ/
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git%3Ba=blob%3Bf=changelog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRVHN3GGVNQWAOL3PWC5FLAV7HUESLZR/
- https://www.chiark.greenend.org.uk/pipermail/adns-announce/2020/000004.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00037.html
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git

# [H] CVE-2017-9105

## Summary
Severity: High
Advisory: CVE-2017-9105
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2017-9105
Type: osv

## Details
An issue was discovered in adns before 1.5.2. It corrupts a pointer when a nameserver speaks first because of a wrong number of pointer dereferences. This bug may well be exploitable as a remote code execution.

## References
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git%3Ba=blob%3Bf=changelog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRVHN3GGVNQWAOL3PWC5FLAV7HUESLZR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGFZ4SPV6KFQK6ZNUZFB5Y32OYFOM5YJ/
- https://www.chiark.greenend.org.uk/pipermail/adns-announce/2020/000004.html
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git

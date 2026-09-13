# [H] CVE-2017-9108

## Summary
Severity: High
Advisory: CVE-2017-9108
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2017-9108
Type: osv

## Details
An issue was discovered in adns before 1.5.2. adnshost mishandles a missing final newline on a stdin read. It is wrong to increment used as well as setting r, since used is incremented according to r, later. Rather one should be doing what read() would have done. Without this fix, adnshost may read and process one byte beyond the buffer, perhaps crashing or perhaps somehow leaking the value of that byte.

## References
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git%3Ba=blob%3Bf=changelog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRVHN3GGVNQWAOL3PWC5FLAV7HUESLZR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGFZ4SPV6KFQK6ZNUZFB5Y32OYFOM5YJ/
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git
- https://www.chiark.greenend.org.uk/pipermail/adns-announce/2020/000004.html

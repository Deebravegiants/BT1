# [C] CVE-2017-9109

## Summary
Severity: Critical
Advisory: CVE-2017-9109
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2017-9109
Type: osv

## Details
An issue was discovered in adns before 1.5.2. It fails to ignore apparent answers before the first RR that was found the first time. when this is fixed, the second answer scan finds the same RRs at the first. Otherwise, adns can be confused by interleaving answers for the CNAME target, with the CNAME itself. In that case the answer data structure (on the heap) can be overrun. With this fixed, it prefers to look only at the answer RRs which come after the CNAME, which is at least arguably correct.

## References
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git%3Ba=blob%3Bf=changelog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRVHN3GGVNQWAOL3PWC5FLAV7HUESLZR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGFZ4SPV6KFQK6ZNUZFB5Y32OYFOM5YJ/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00037.html
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git
- https://www.chiark.greenend.org.uk/pipermail/adns-announce/2020/000004.html

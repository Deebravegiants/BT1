# [C] CVE-2016-9400

## Summary
Severity: Critical
Advisory: CVE-2016-9400
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-22
Source: https://osv.dev/vulnerability/CVE-2016-9400
Type: osv

## Details
The CClient::ProcessServerPacket method in engine/client/client.cpp in Teeworlds before 0.6.4 allows remote servers to write to arbitrary physical memory locations and possibly execute arbitrary code via vectors involving snap handling.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C4JNSBXXPE7O32ZMFK7D7YL6EKLG7PRV/
- http://www.securityfocus.com/bid/94381
- https://security.gentoo.org/glsa/201705-13
- https://www.teeworlds.com/?page=news&id=12086
- http://www.openwall.com/lists/oss-security/2016/11/16/8
- http://www.openwall.com/lists/oss-security/2016/11/17/8
- https://github.com/teeworlds/teeworlds/commit/ff254722a2683867fcb3e67569ffd36226c4bc62

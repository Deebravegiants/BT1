# [H] CVE-2018-7999

## Summary
Severity: High
Advisory: CVE-2018-7999
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-7999
Type: osv

## Details
In libgraphite2 in graphite2 1.3.11, a NULL pointer dereference vulnerability was found in Segment.cpp during a dumbRendering operation, which may allow attackers to cause a denial of service or possibly have unspecified other impact via a crafted .ttf file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L5F3CK2IPXFCLQZEBEEXONWIABN2E7H2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LVWOKYZZDEMG6VSG53KAGUOHUIIQ7CND/
- https://github.com/silnrsi/graphite/commit/db132b4731a9b4c9534144ba3a18e65b390e9ff6
- https://github.com/silnrsi/graphite/issues/22

# [H] CVE-2017-15377

## Summary
Severity: High
Advisory: CVE-2017-15377
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-23
Source: https://osv.dev/vulnerability/CVE-2017-15377
Type: osv

## Details
In Suricata before 4.x, it was possible to trigger lots of redundant checks on the content of crafted network traffic with a certain signature, because of DetectEngineContentInspection in detect-engine-content-inspection.c. The search engine doesn't stop when it should after no match is found; instead, it stops only upon reaching inspection-recursion-limit (3000 by default).

## References
- https://lists.debian.org/debian-lts-announce/2018/12/msg00000.html
- https://redmine.openinfosecfoundation.org/issues/2231
- https://github.com/OISF/suricata/commit/b9579fbe7dd408200ef03cbe20efddb624b73885

# [H] CVE-2020-7238

## Summary
Severity: High
Advisory: CVE-2020-7238
Aliases: GHSA-ff2w-cq2g-wv5f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/CVE-2020-7238
Type: osv

## Details
Netty 4.1.43.Final allows HTTP Request Smuggling because it mishandles Transfer-Encoding whitespace (such as a [space]Transfer-Encoding:chunked line) and a later Content-Length header. This issue exists because of an incomplete fix for CVE-2019-16869.

## References
- https://lists.apache.org/thread.html/r131e572d003914843552fa45c4398b9903fb74144986e8b107c0a3a7%40%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/rc8d554aad889d12b140d9fd7d2d6fc2e8716e9792f6f4e4b2cdc2d05%40%3Ccommits.cassandra.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TS6VX7OMXPDJIU5LRGUAHRK6MENAVJ46/
- https://access.redhat.com/errata/RHSA-2020:0497
- https://access.redhat.com/errata/RHSA-2020:0567
- https://access.redhat.com/errata/RHSA-2020:0601
- https://access.redhat.com/errata/RHSA-2020:0605
- https://access.redhat.com/errata/RHSA-2020:0606
- https://access.redhat.com/errata/RHSA-2020:0804
- https://access.redhat.com/errata/RHSA-2020:0805
- https://access.redhat.com/errata/RHSA-2020:0806
- https://access.redhat.com/errata/RHSA-2020:0811
- https://lists.debian.org/debian-lts-announce/2020/02/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00003.html
- https://netty.io/news/
- https://www.debian.org/security/2021/dsa-4885
- https://github.com/jdordonezn/CVE-2020-72381/issues/1

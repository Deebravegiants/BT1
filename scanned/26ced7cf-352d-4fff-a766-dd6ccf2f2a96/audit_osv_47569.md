# [M] CVE-2016-8605

## Summary
Severity: Medium
Advisory: CVE-2016-8605
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-01-12
Source: https://osv.dev/vulnerability/CVE-2016-8605
Type: osv

## Details
The mkdir procedure of GNU Guile temporarily changed the process' umask to zero. During that time window, in a multithreaded application, other threads could end up creating files with insecure permissions. For example, mkdir without the optional mode argument would create directories as 0777. This is fixed in Guile 2.0.13. Prior versions are affected.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UJP5S36GTXMDEBXWF6LKKV76DSLNQG44/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6QTAGSDCTYXTABAA77BQJGNKOOBRV4DK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FNVE5N24FLWDYBQ3LAFMF6BFCWKDO7VM/
- http://www.securityfocus.com/bid/93510
- http://www.openwall.com/lists/oss-security/2016/10/12/1

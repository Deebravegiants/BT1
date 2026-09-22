# [H] CVE-2015-8547

## Summary
Severity: High
Advisory: CVE-2015-8547
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-8547
Type: osv

## Details
The CoreUserInputHandler::doMode function in core/coreuserinputhandler.cpp in Quassel 0.10.0 allows remote attackers to cause a denial of service (application crash) via the "/op *" command in a query.

## References
- https://github.com/quassel/quassel/commit/b8edbda019eeb99da8663193e224efc9d1265dc7
- https://github.com/quassel/quassel/pull/153
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174938.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174976.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00099.html
- http://www.openwall.com/lists/oss-security/2015/12/12/1
- http://www.openwall.com/lists/oss-security/2015/12/13/1

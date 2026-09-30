# [H] CVE-2011-1755

## Summary
Severity: High
Advisory: CVE-2011-1755
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2011-06-21
Source: https://osv.dev/vulnerability/CVE-2011-1755
Type: osv

## Details
jabberd2 before 2.2.14 does not properly detect recursion during entity expansion, which allows remote attackers to cause a denial of service (memory and CPU consumption) via a crafted XML document containing a large number of nested entity references, a similar issue to CVE-2003-1564.

## References
- http://secunia.com/advisories/44787
- http://secunia.com/advisories/44957
- http://secunia.com/advisories/45112
- http://support.apple.com/kb/HT5002
- http://www.mail-archive.com/jabberd2%40lists.xiaoka.com/msg01655.html
- http://www.securityfocus.com/bid/48250
- https://exchange.xforce.ibmcloud.com/vulnerabilities/67770
- http://lists.apple.com/archives/Security-announce/2011//Oct/msg00003.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-June/061341.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-June/061458.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-June/061482.html
- https://bugzilla.redhat.com/show_bug.cgi?id=700390
- https://bugzilla.redhat.com/show_bug.cgi?id=700390
- http://codex.xiaoka.com/svn/jabberd2/tags/jabberd-2.2.14/ChangeLog
- http://www.redhat.com/support/errata/RHSA-2011-0881.html
- http://www.redhat.com/support/errata/RHSA-2011-0882.html
- http://www.securityfocus.com/bid/48250
- https://hermes.opensuse.org/messages/9197650

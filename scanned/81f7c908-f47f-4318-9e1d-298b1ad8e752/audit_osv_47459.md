# [M] CVE-2016-5410

## Summary
Severity: Medium
Advisory: CVE-2016-5410
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2016-5410
Type: osv

## Details
firewalld.py in firewalld before 0.4.3.3 allows local users to bypass authentication and modify firewall configurations via the (1) addPassthrough, (2) removePassthrough, (3) addEntry, (4) removeEntry, or (5) setEntries D-Bus API method.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DPM3GUQRU2KPRXDEQLAMCDQEAIARJSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBJMYLGRVKIPJEI3VZJ4WQZT7FBQ5BKO/
- https://security.gentoo.org/glsa/201701-70
- http://rhn.redhat.com/errata/RHSA-2016-2597.html
- http://www.securityfocus.com/bid/92481
- http://www.firewalld.org/2016/08/firewalld-0-4-3-3-release
- https://bugzilla.redhat.com/show_bug.cgi?id=1360135
- http://www.openwall.com/lists/oss-security/2016/08/16/3

# [M] CVE-2014-8171

## Summary
Severity: Medium
Advisory: CVE-2014-8171
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2014-8171
Type: osv

## Details
The memory resource controller (aka memcg) in the Linux kernel allows local users to cause a denial of service (deadlock) by spawning new processes within a memory-constrained cgroup.

## References
- http://rhn.redhat.com/errata/RHSA-2015-0864.html
- http://rhn.redhat.com/errata/RHSA-2015-2152.html
- http://rhn.redhat.com/errata/RHSA-2015-2411.html
- http://rhn.redhat.com/errata/RHSA-2016-0068.html
- http://www.securityfocus.com/bid/74293
- https://bugzilla.redhat.com/show_bug.cgi?id=1198109
- https://bugzilla.redhat.com/show_bug.cgi?id=1198109

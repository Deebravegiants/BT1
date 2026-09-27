# [H] CVE-2016-9579

## Summary
Severity: High
Advisory: CVE-2016-9579
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-9579
Type: osv

## Details
A flaw was found in the way Ceph Object Gateway would process cross-origin HTTP requests if the CORS policy was set to allow origin on a bucket. A remote unauthenticated attacker could use this flaw to cause denial of service by sending a specially-crafted cross-origin HTTP request. Ceph branches 1.3.x and 2.x are affected.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2994.html
- http://rhn.redhat.com/errata/RHSA-2016-2995.html
- http://www.securityfocus.com/bid/94936
- http://rhn.redhat.com/errata/RHSA-2016-2954.html
- http://rhn.redhat.com/errata/RHSA-2016-2956.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9579
- http://tracker.ceph.com/issues/18187

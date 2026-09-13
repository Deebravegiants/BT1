# [M] CVE-2016-8626

## Summary
Severity: Medium
Advisory: CVE-2016-8626
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-31
Source: https://osv.dev/vulnerability/CVE-2016-8626
Type: osv

## Details
A flaw was found in Red Hat Ceph before 0.94.9-8. The way Ceph Object Gateway handles POST object requests permits an authenticated attacker to launch a denial of service attack by sending null or specially crafted POST object requests.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2847.html
- http://rhn.redhat.com/errata/RHSA-2016-2848.html
- http://www.securityfocus.com/bid/94488
- http://rhn.redhat.com/errata/RHSA-2016-2815.html
- http://rhn.redhat.com/errata/RHSA-2016-2816.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8626
- http://tracker.ceph.com/issues/17635

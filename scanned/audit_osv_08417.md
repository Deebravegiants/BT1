# [H] CVE-2016-3108

## Summary
Severity: High
Advisory: CVE-2016-3108
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2016-3108
Type: osv

## Details
The pulp-gen-nodes-certificate script in Pulp before 2.8.3 allows local users to leak the keys or write to arbitrary files via a symlink attack.

## References
- http://www.openwall.com/lists/oss-security/2016/05/20/1
- https://access.redhat.com/errata/RHBA-2016:1501
- https://bugzilla.redhat.com/attachment.cgi?id=1146475
- https://bugzilla.redhat.com/show_bug.cgi?id=1325934
- https://github.com/pulp/pulp/pull/2528
- https://pulp.plan.io/issues/1830

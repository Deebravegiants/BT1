# [M] CVE-2017-15121

## Summary
Severity: Medium
Advisory: CVE-2017-15121
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-07
Source: https://osv.dev/vulnerability/CVE-2017-15121
Type: osv

## Details
A non-privileged user is able to mount a fuse filesystem on RHEL 6 or 7 and crash a system if an application punches a hole in a file that does not end aligned to a page boundary.

## References
- https://support.f5.com/csp/article/K42142782?utm_source=f5support&amp%3Butm_medium=RSS
- http://www.securityfocus.com/bid/102128
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2018:1854
- https://bugzilla.redhat.com/show_bug.cgi?id=1520893

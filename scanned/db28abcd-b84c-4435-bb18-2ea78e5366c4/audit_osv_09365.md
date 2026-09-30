# [M] CVE-2016-9595

## Summary
Severity: Medium
Advisory: CVE-2016-9595
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2016-9595
Type: osv

## Details
A flaw was found in katello-debug before 3.4.0 where certain scripts and log files used insecure temporary files. A local user could exploit this flaw to conduct a symbolic-link attack, allowing them to overwrite the contents of arbitrary files.

## References
- https://access.redhat.com/errata/RHSA-2018:0336
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9595

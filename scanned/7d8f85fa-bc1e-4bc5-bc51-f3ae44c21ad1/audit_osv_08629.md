# [M] CVE-2016-4995

## Summary
Severity: Medium
Advisory: CVE-2016-4995
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-08-19
Source: https://osv.dev/vulnerability/CVE-2016-4995
Type: osv

## Details
Foreman before 1.11.4 and 1.12.x before 1.12.1 does not properly restrict access to preview provisioning templates, which allows remote authenticated users with permission to view some hosts to obtain sensitive host configuration information via a URL with a hostname.

## References
- https://access.redhat.com/errata/RHSA-2018:0336
- https://theforeman.org/security.html#2016-4995
- http://projects.theforeman.org/issues/15490
- http://projects.theforeman.org/projects/foreman/repository/revisions/c3c186de12be15e55d9582e54659f765304a1073

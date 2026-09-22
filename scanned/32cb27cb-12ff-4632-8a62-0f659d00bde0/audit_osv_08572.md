# [M] CVE-2016-4451

## Summary
Severity: Medium
Advisory: CVE-2016-4451
CVSS: 5.0 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-08-19
Source: https://osv.dev/vulnerability/CVE-2016-4451
Type: osv

## Details
The (1) Organization and (2) Locations APIs in Foreman before 1.11.3 and 1.12.x before 1.12.0-RC1 allow remote authenticated users with unlimited filters to bypass organization and location restrictions and read or modify data for an arbitrary organization by leveraging knowledge of the id of that organization.

## References
- http://projects.theforeman.org/issues/15182
- https://access.redhat.com/errata/RHSA-2018:0336
- https://theforeman.org/security.html#2016-4451
- http://projects.theforeman.org/projects/foreman/repository/revisions/1144040f444b4bf4aae81940a150b26b23b4623c

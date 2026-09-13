# [M] CVE-2018-14432

## Summary
Severity: Medium
Advisory: CVE-2018-14432
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-31
Source: https://osv.dev/vulnerability/CVE-2018-14432
Type: osv

## Details
In the Federation component of OpenStack Keystone before 11.0.4, 12.0.0, and 13.0.0, an authenticated "GET /v3/OS-FEDERATION/projects" request may bypass intended access restrictions on listing projects. An authenticated user may discover projects they have no authority to access, leaking all projects in the deployment and their attributes. Only Keystone with the /v3/OS-FEDERATION endpoint enabled via policy.json is affected.

## References
- http://www.securityfocus.com/bid/104930
- https://access.redhat.com/errata/RHSA-2018:2523
- https://access.redhat.com/errata/RHSA-2018:2533
- https://access.redhat.com/errata/RHSA-2018:2543
- https://www.debian.org/security/2018/dsa-4275
- http://www.openwall.com/lists/oss-security/2018/07/25/2

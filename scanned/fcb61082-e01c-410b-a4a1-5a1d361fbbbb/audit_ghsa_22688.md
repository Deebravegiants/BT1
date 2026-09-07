# [M] OpenStack Image Service (Glance) vulnerable to Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-5xrj-ghhp-hx7p
CVE: CVE-2016-0757
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5xrj-ghhp-hx7p
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=11.0.0 <11.0.2

## Details
OpenStack Image Service (Glance) before 2015.1.3 (kilo) and 11.0.x before 11.0.2 (liberty), when show_multiple_locations is enabled, allow remote authenticated users to change image status and upload new image data by removing the last location of an image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0757
- https://access.redhat.com/errata/RHSA-2016:0309
- https://access.redhat.com/errata/RHSA-2016:0352
- https://access.redhat.com/errata/RHSA-2016:0354
- https://access.redhat.com/errata/RHSA-2016:0358
- https://access.redhat.com/security/cve/CVE-2016-0757
- https://bugzilla.redhat.com/show_bug.cgi?id=1302607
- https://opendev.org/openstack/glance
- https://rhn.redhat.com/errata/RHSA-2016-0309.html
- https://security.openstack.org/ossa/OSSA-2016-006.html
- https://web.archive.org/web/20210123081823/https://www.securityfocus.com/bid/82696

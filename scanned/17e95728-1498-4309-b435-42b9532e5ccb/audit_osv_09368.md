# [M] CVE-2016-9598

## Summary
Severity: Medium
Advisory: CVE-2016-9598
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-16
Source: https://osv.dev/vulnerability/CVE-2016-9598
Type: osv

## Details
libxml2, as used in Red Hat JBoss Core Services, allows context-dependent attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted XML document. NOTE: this vulnerability exists because of a missing fix for CVE-2016-4483.

## References
- https://access.redhat.com/errata/RHSA-2018:2486
- https://bugzilla.redhat.com/show_bug.cgi?id=1408306

# [C] CVE-2019-11934

## Summary
Severity: Critical
Advisory: CVE-2019-11934
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-11934
Type: osv

## Details
Improper handling of close_notify alerts can result in an out-of-bounds read in AsyncSSLSocket. This issue affects folly prior to v2019.11.04.00.

## References
- https://www.facebook.com/security/advisories/cve-2019-11934
- https://github.com/facebook/folly/commit/c321eb588909646c15aefde035fd3133ba32cdee

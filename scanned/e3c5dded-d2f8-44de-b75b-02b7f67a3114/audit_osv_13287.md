# [M] CVE-2018-19110

## Summary
Severity: Medium
Advisory: CVE-2018-19110
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19110
Type: osv

## Details
The skin-management feature in tianti 2.3 allows remote authenticated users to bypass intended permission restrictions by visiting tianti-module-admin/user/skin/list directly because controller\usercontroller.java maps a /skin/list request to the function skinList, and lacks an authorization check.

## References
- https://github.com/xujeff/tianti/issues/29

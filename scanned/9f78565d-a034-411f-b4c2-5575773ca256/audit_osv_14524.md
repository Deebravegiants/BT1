# [M] CVE-2019-1010084

## Summary
Severity: Medium
Advisory: CVE-2019-1010084
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-1010084
Type: osv

## Details
Dancer::Plugin::SimpleCRUD 1.14 and earlier is affected by: Incorrect Access Control. The impact is: Potential for unathorised access to data. The component is: Incorrect calls to _ensure_auth() wrapper result in authentication-checking not being applied to al routes.

## References
- https://github.com/bigpresh/Dancer-Plugin-SimpleCRUD/pull/109

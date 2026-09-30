# [C] CVE-2020-1916

## Summary
Severity: Critical
Advisory: CVE-2020-1916
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2020-1916
Type: osv

## Details
An incorrect size calculation in ldap_escape may lead to an integer overflow when overly long input is passed in, resulting in an out-of-bounds write. This issue affects HHVM prior to 4.56.2, all versions between 4.57.0 and 4.78.0, 4.79.0, 4.80.0, 4.81.0, 4.82.0, 4.83.0.

## References
- https://hhvm.com/blog/2020/11/12/security-update.html
- https://github.com/facebook/hhvm/commit/abe0b29e4d3a610f9bc920b8be4ad8403364c2d4

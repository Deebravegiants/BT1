# [M] CVE-2021-38751

## Summary
Severity: Medium
Advisory: CVE-2021-38751
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-08-16
Source: https://osv.dev/vulnerability/CVE-2021-38751
Type: osv

## Details
A HTTP Host header attack exists in ExponentCMS 2.6 and below in /exponent_constants.php. A modified HTTP header can change links on the webpage to an arbitrary value, leading to a possible attack vector for MITM.

## References
- https://github.com/exponentcms/exponent-cms/issues/1544

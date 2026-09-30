# [M] CVE-2018-14836

## Summary
Severity: Medium
Advisory: CVE-2018-14836
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-02
Source: https://osv.dev/vulnerability/CVE-2018-14836
Type: osv

## Details
Subrion 4.2.1 is vulnerable to Improper Access control because user groups not having access to the Admin panel are able to access it (but not perform actions) if the Guests user group has access to the Admin panel.

## References
- https://github.com/intelliants/subrion/issues/762

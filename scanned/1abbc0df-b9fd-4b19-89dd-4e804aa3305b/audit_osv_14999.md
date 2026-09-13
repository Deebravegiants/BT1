# [M] CVE-2019-12902

## Summary
Severity: Medium
Advisory: CVE-2019-12902
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-12902
Type: osv

## Details
Pydio Cells before 1.5.0 does incomplete cleanup of a user's data upon deletion. This allows a new user, holding the same User ID as a deleted user, to restore the deleted user's data.

## References
- https://pydio.com/en/community/releases/pydio-cells/pydio-cells-150-performances-features-security
- https://research.loginsoft.com/vulnerability/multiple-vulnerabilities-in-pydio-cells-1-4-1/

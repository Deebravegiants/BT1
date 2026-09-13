# [M] CVE-2019-12903

## Summary
Severity: Medium
Advisory: CVE-2019-12903
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-12903
Type: osv

## Details
Pydio Cells before 1.5.0, when supplied with a Name field in an unexpected Unicode format, fails to handle this and includes the database column/table name as pert of the error message, exposing sensitive information.

## References
- https://pydio.com/en/community/releases/pydio-cells/pydio-cells-150-performances-features-security
- https://research.loginsoft.com/vulnerability/multiple-vulnerabilities-in-pydio-cells-1-4-1/

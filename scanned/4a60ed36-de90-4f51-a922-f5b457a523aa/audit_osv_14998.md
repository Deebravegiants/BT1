# [H] CVE-2019-12901

## Summary
Severity: High
Advisory: CVE-2019-12901
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-12901
Type: osv

## Details
Pydio Cells before 1.5.0 fails to neutralize '../' elements, allowing an attacker with minimum privilege to Upload files to, and Delete files/folders from, an unprivileged directory, leading to Privilege escalation.

## References
- https://pydio.com/en/community/releases/pydio-cells/pydio-cells-150-performances-features-security
- https://research.loginsoft.com/vulnerability/multiple-vulnerabilities-in-pydio-cells-1-4-1/

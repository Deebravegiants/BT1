# [M] CVE-2020-9329

## Summary
Severity: Medium
Advisory: CVE-2020-9329
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-02-21
Source: https://osv.dev/vulnerability/CVE-2020-9329
Type: osv

## Details
Gogs through 0.11.91 allows attackers to violate the admin-specified repo-creation policy due to an internal/db/repo.go race condition.

## References
- https://github.com/gogs/gogs/issues/5926

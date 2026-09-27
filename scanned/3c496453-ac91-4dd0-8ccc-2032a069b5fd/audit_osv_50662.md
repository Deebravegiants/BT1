# [C] CVE-2020-27637

## Summary
Severity: Critical
Advisory: CVE-2020-27637
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/CVE-2020-27637
Type: osv

## Details
The R programming language’s default package manager CRAN is affected by a path traversal vulnerability that can lead to server compromise. This vulnerability affects packages installed via the R CMD install cli command or the install.packages() function from the interpreter. Update to version 4.0.3

## References
- https://security.gentoo.org/glsa/202401-07
- https://www.r-project.org/foundation/
- https://labs.bishopfox.com/advisories/cran-version-4.0.2

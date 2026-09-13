# [H] CVE-2019-16767

## Summary
Severity: High
Advisory: CVE-2019-16767
Aliases: GHSA-g654-5qjf-g6cx
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-16767
Type: osv

## Details
The admin sys mode is now conditional and dedicated for the special case. By default, since ezmaster@5.2.11 no instance (container) is launched with advanced capabilities (not launched as root)

## References
- https://github.com/Inist-CNRS/ezmaster/blob/master/CHANGELOG.md#ezmaster-5211
- https://github.com/Inist-CNRS/ezmaster/security/advisories/GHSA-g654-5qjf-g6cx
- https://github.com/Inist-CNRS/ezmaster/pull/51

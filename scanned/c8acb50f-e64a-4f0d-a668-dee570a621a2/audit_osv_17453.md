# [M] CVE-2020-15217

## Summary
Severity: Medium
Advisory: CVE-2020-15217
Aliases: GHSA-x9hg-j29f-wvvv
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-10-07
Source: https://osv.dev/vulnerability/CVE-2020-15217
Type: osv

## Details
In GLPI before version 9.5.2, there is a leakage of user information through the public FAQ. The issue was introduced in version 9.5.0 and patched in 9.5.2. As a workaround, disable public access to the FAQ.

## References
- https://github.com/glpi-project/glpi/security/advisories/GHSA-x9hg-j29f-wvvv
- https://github.com/glpi-project/glpi/commit/39e25591efddc560e3679ab07e443ee6198705e2

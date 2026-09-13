# [C] CVE-2021-43616

## Summary
Severity: Critical
Advisory: CVE-2021-43616
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-13
Source: https://osv.dev/vulnerability/CVE-2021-43616
Type: osv

## Details
The npm ci command in npm 7.x and 8.x through 8.1.3 proceeds with an installation even if dependency information in package-lock.json differs from package.json. This behavior is inconsistent with the documentation, and makes it easier for attackers to install malware that was supposed to have been blocked by an exact version match requirement in package-lock.json. NOTE: The npm team believes this is not a vulnerability. It would require someone to socially engineer package.json which has different dependencies than package-lock.json. That user would have to have file system or write access to change dependencies. The npm team states preventing malicious actors from socially engineering or gaining file system access is outside the scope of the npm CLI.

## References
- https://docs.npmjs.com/cli/v8/commands/npm-ci
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NXNVFKOF5ZYH5NIRWHKN6O6UBCHDV6FE/
- https://docs.npmjs.com/cli/v7/commands/npm-ci
- https://github.com/icatalina/CVE-2021-43616
- https://security.netapp.com/advisory/ntap-20211210-0002/
- https://github.com/npm/cli/issues/2701
- https://github.com/npm/cli/issues/2701#issuecomment-972900511
- https://github.com/npm/cli/issues/2701#issuecomment-979054224
- https://github.com/npm/cli/commit/457e0ae61bbc55846f5af44afa4066921923490f
- https://medium.com/cider-sec/this-time-we-were-lucky-85c0dcac94a0

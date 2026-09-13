# [H] CVE-2021-29468

## Summary
Severity: High
Advisory: CVE-2021-29468
Aliases: GHSA-rmp3-wq55-f557
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-29468
Type: osv

## Details
Cygwin Git is a patch set for the git command line tool for the cygwin environment. A specially crafted repository that contains symbolic links as well as files with backslash characters in the file name may cause just-checked out code to be executed while checking out a repository using Git on Cygwin. The problem will be patched in the Cygwin Git v2.31.1-2 release. At time of writing, the vulnerability is present in the upstream Git source code; any Cygwin user who compiles Git for themselves from upstream sources should manually apply a patch to mitigate the vulnerability. As mitigation users should not clone or pull from repositories from untrusted sources. CVE-2019-1354 was an equivalent vulnerability in Git for Visual Studio.

## References
- https://lore.kernel.org/git/CA+kUOa=juEdBMVr_gyTKjz7PkPt2DZHkXQyzcQmAWCsEHC_ssw%40mail.gmail.com/T/#u
- https://cygwin.com/pipermail/cygwin-announce/2021-April/010018.html
- https://github.com/me-and/Cygwin-Git/blob/main/check-backslash-safety.patch
- https://github.com/me-and/Cygwin-Git/security/advisories/GHSA-rmp3-wq55-f557

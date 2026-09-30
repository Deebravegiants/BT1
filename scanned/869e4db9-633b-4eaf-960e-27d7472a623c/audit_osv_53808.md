# [M] CVE-2023-26112

## Summary
Severity: Medium
Advisory: CVE-2023-26112
Aliases: GHSA-c33w-24p9-8m24, PYSEC-2026-1270
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-03
Source: https://osv.dev/vulnerability/CVE-2023-26112
Type: osv

## Details
All versions of the package configobj are vulnerable to Regular Expression Denial of Service (ReDoS) via the validate function, using (.+?)\((.*)\).**Note:** This is only exploitable in the case of a developer, putting the offending value in a server side configuration file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6BO4RLMYEJODCNUE3DJIIUUFVTPAG6VN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NZHY7B33EFY4LESP2NI4APQUPRROTAZK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PYU4IHVLOTYMFPH7KDOJGKZQR4GKWPFK/
- https://github.com/DiffSK/configobj/issues/232
- https://security.snyk.io/vuln/SNYK-PYTHON-CONFIGOBJ-3252494

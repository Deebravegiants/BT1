# [H] Apache Subversion: Command line argument injection on Windows platforms

## Summary
Severity: High
Advisory: BIT-subversion-2024-45720
Aliases: CVE-2024-45720
Ecosystem: Bitnami
Published: 2024-10-11
Source: https://osv.dev/vulnerability/BIT-subversion-2024-45720
Type: osv

## Affected
- Bitnami: `subversion` — affected >=1.0.0 <1.14.4

## Details
On Windows platforms, a "best fit" character encoding conversion of command line arguments to Subversion's executables (e.g., svn.exe, etc.) may lead to unexpected command line argument interpretation, including argument injection and execution of other programs, if a specially crafted command line argument string is processed.

All versions of Subversion up to and including Subversion 1.14.3 are affected on Windows platforms only. Users are recommended to upgrade to version Subversion 1.14.4, which fixes this issue.

Subversion is not affected on UNIX-like platforms.

## References
- https://subversion.apache.org/security/CVE-2024-45720-advisory.txt
- http://www.openwall.com/lists/oss-security/2024/10/08/3
- https://nvd.nist.gov/vuln/detail/CVE-2024-45720

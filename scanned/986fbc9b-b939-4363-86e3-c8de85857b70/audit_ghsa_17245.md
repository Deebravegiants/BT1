# [C] Robocode vulnerable to Directory Traversal in recursivelyDelete Method

## Summary
Severity: Critical
Advisory: GHSA-j8r2-47rx-qhw4
CVE: CVE-2025-14306
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/AU:Y/R:U/V:D/RE:M/U:Red (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-j8r2-47rx-qhw4
Type: github-advisory

## Affected
- Maven: `net.sf.robocode:robocode.core` — affected >=0 <1.9.5.6

## Details
A directory traversal vulnerability exists in the CacheCleaner component of Robocode version 1.9.3.6. The recursivelyDelete method fails to properly sanitize file paths, allowing attackers to traverse directories and delete arbitrary files on the system. This vulnerability can be exploited by submitting specially crafted inputs that manipulate the file path, leading to potential unauthorized file deletions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14306
- https://github.com/robo-code/robocode/pull/67
- https://github.com/robo-code/robocode/commit/26b6ba8ed5b2a11a646ce2d5da8d42cd53574b1f
- https://github.com/robo-code/robocode

# [M] Apache Helix UI vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-mhxg-2xf7-4xwx
CVE: CVE-2022-47500
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-mhxg-2xf7-4xwx
Type: github-advisory

## Affected
- Maven: `org.apache.helix:helix` — affected >=0.8.0 <1.1.0

## Details
URL Redirection to Untrusted Site ('Open Redirect') vulnerability in Apache Software Foundation Apache Helix UI component.This issue affects Apache Helix all releases from 0.8.0 to and including 1.0.4. Solution: removed the the forward component since it was improper designed for UI embedding. User please upgrade to 1.1.0 to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47500
- https://github.com/apache/helix
- https://lists.apache.org/thread/lr74xtxxbb1t3dfn5qzzwl2xjr3qlbmh

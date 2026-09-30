# [H] easy-rules-mvel vulnerable to remote code execution

## Summary
Severity: High
Advisory: GHSA-fgwc-3j6w-ch22
CVE: CVE-2023-50571
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-29
Source: https://github.com/advisories/GHSA-fgwc-3j6w-ch22
Type: github-advisory

## Affected
- Maven: `org.jeasy:easy-rules-mvel` — affected 4.1.0

## Details
easy-rules-mvel v4.1.0 was discovered to contain a remote code execution (RCE) vulnerability via the component `mVELRule`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50571
- https://github.com/j-easy/easy-rules/issues/419
- https://github.com/j-easy/easy-rules

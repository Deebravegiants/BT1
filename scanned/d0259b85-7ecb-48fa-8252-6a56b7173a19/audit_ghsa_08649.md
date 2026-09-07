# [M] fast-xml-builder Comment Value regex can be bypassed

## Summary
Severity: Medium
Advisory: GHSA-45c6-75p6-83cc
CVE: CVE-2026-44664
CWE: CWE-91
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-45c6-75p6-83cc
Type: github-advisory

## Affected
- npm: `fast-xml-builder` — affected >=1.1.5 <1.1.6

## Details
# Summary
The fix for https://github.com/advisories/GHSA-gh4j-gqv2-49f6 in fast-xml-parser sanitizes `--` sequences in XML comment content using .replace(/--/g, '- -'). This skip the values containing three consecutive dashes (e.g., --->...), allowing an attacker to break out of an XML comment and inject arbitrary XML/HTML content.

### Impact
Any application with comment property enabled allow attacker to inject malicious or unwanted code like JS script tag in the XML/HTML output.

### Workarounds
Check for the presence of 3 consecutive dashes externally in the property value used for comment tag.

## References
- https://github.com/NaturalIntelligence/fast-xml-builder/security/advisories/GHSA-45c6-75p6-83cc
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-gh4j-gqv2-49f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-44664
- https://github.com/NaturalIntelligence/fast-xml-builder

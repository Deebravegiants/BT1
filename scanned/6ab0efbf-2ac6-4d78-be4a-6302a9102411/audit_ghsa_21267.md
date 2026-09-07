# [M] HyperDown vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-4r9g-w48q-8jwm
CVE: CVE-2022-25849
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-4r9g-w48q-8jwm
Type: github-advisory

## Affected
- Packagist: `joyqi/hyper-down` — affected >=0

## Details
HyperDown is a markdown parser written for the Chinese website SegmentFault. Improper validation of the href attribute allows for Cross-site Scripting. At publication there are no patched versions, and no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25849
- https://github.com/SegmentFault/HyperDown
- https://security.snyk.io/vuln/SNYK-PHP-JOYQIHYPERDOWN-2953544

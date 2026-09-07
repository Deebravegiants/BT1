# [M] Path Traversal in LemMinX

## Summary
Severity: Medium
Advisory: GHSA-gggp-gh2p-996x
CVE: CVE-2022-0673
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-gggp-gh2p-996x
Type: github-advisory

## Affected
- Maven: `org.eclipse.lemminx:lemminx-parent` — affected >=0 <0.19.0

## Details
A flaw was found in LemMinX in versions prior to 0.19.0. Cache poisoning of external schema files is possible due to directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0673
- https://github.com/eclipse/lemminx/pull/1171
- https://github.com/eclipse/lemminx
- https://github.com/eclipse/lemminx/blob/master/CHANGELOG.md#0190-february-14-2022

# [M] Exposure of Sensitive Information to an Unauthorized Actor in LemMinX

## Summary
Severity: Medium
Advisory: GHSA-hrxv-694f-22g3
CVE: CVE-2022-0672
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-hrxv-694f-22g3
Type: github-advisory

## Affected
- Maven: `org.eclipse.lemminx:lemminx-parent` — affected >=0 <0.19.0

## Details
A flaw was found in LemMinX in versions prior to 0.19.0. Insecure redirect could allow unauthorized access to sensitive information locally if LemMinX is run under a privileged user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0672
- https://github.com/eclipse/lemminx/pull/1174
- https://github.com/eclipse/lemminx/commit/076b88052c2a63f60a98ef4b45e3e38c217b70ae
- https://github.com/eclipse/lemminx
- https://github.com/eclipse/lemminx/blob/master/CHANGELOG.md#0190-february-14-2022

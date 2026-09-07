# [M] Cross-Site Scripting in simple-markdown

## Summary
Severity: Medium
Advisory: GHSA-qj3f-9gmq-fwv5
CVE: CVE-2019-9844
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-09
Source: https://github.com/advisories/GHSA-qj3f-9gmq-fwv5
Type: github-advisory

## Affected
- npm: `simple-markdown` — affected >=0 <0.4.4

## Details
Versions of `simple-markdown` prior to 0.4.4 are vulnerable to Cross-Site Scripting. Due to insufficient input sanitization the package may render output containing malicious JavaScript. This vulnerability can be exploited through input of links containing `data` or VBScript URIs and a base64-encoded payload.


## Recommendation

Upgrade to version 0.4.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9844
- https://github.com/Khan/simple-markdown/pull/63
- https://github.com/Khan/simple-markdown
- https://github.com/advisories/GHSA-qj3f-9gmq-fwv5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JFLP3KJVSV5VWMNEBRXLGRVYFXOV5KOG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KZG2I7VH7WLSEUQ77KYP5CRAVFT2RK2U
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O5EFW655O3BXZYAPB65XEREXB2DSNSOT
- https://www.npmjs.com/advisories/815
- https://www.npmjs.com/package/simple-markdown/v/0.4.4

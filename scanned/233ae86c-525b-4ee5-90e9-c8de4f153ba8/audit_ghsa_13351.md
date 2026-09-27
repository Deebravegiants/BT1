# [C] Code injection in webmagic-core

## Summary
Severity: Critical
Advisory: GHSA-grvq-vjqr-x8vm
CVE: CVE-2023-39015
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-grvq-vjqr-x8vm
Type: github-advisory

## Affected
- Maven: `us.codecraft:webmagic-core` — affected >=0

## Details
webmagic-extension v0.9.0 and below was discovered to contain a code injection vulnerability via the component us.codecraft.webmagic.downloader.PhantomJSDownloader.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39015
- https://github.com/code4craft/webmagic/issues/1122
- https://github.com/code4craft/webmagic

# [M] Use-After-Free in puppeteer

## Summary
Severity: Medium
Advisory: GHSA-c2gp-86p4-5935
CVE: CVE-2019-5786
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-c2gp-86p4-5935
Type: github-advisory

## Affected
- npm: `puppeteer` — affected >=0 <1.13.0

## Details
Versions of `puppeteer` prior to 1.13.0 are vulnerable to the Use-After-Free vulnerability in Chromium (CVE-2019-5786). The Chromium FileReader API is vulnerable to Use-After-Free which may lead to Remote Code Execution.


## Recommendation

Upgrade to version 1.13.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5786
- https://github.com/GoogleChrome/puppeteer/issues/4141
- https://blog.exodusintel.com/2019/03/20/cve-2019-5786-analysis-and-exploitation
- https://chromereleases.googleblog.com/2019/03/stable-channel-update-for-desktop.html
- https://crbug.com/936448
- https://github.com/GoogleChrome/puppeteer
- https://snyk.io/vuln/SNYK-JS-PUPPETEER-174321
- https://www.npmjs.com/advisories/824

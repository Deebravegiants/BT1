# [C] Prototype Pollution in minimist

## Summary
Severity: Critical
Advisory: GHSA-xvch-5gv4-984h
CVE: CVE-2021-44906
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-xvch-5gv4-984h
Type: github-advisory

## Affected
- npm: `minimist` — affected >=1.0.0 <1.2.6
- npm: `minimist` — affected >=0 <0.2.4

## Details
Minimist prior to 1.2.6 and 0.2.4 is vulnerable to Prototype Pollution via file `index.js`, function `setKey()` (lines 69-95).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44906
- https://github.com/minimistjs/minimist/issues/11
- https://github.com/substack/minimist/issues/164
- https://github.com/minimistjs/minimist/pull/24
- https://github.com/minimistjs/minimist/commit/34e20b8461118608703d6485326abbb8e35e1703
- https://github.com/minimistjs/minimist/commit/bc8ecee43875261f4f17eb20b1243d3ed15e70eb
- https://github.com/minimistjs/minimist/commit/c2b981977fa834b223b408cfb860f933c9811e4d
- https://github.com/minimistjs/minimist/commit/ef9153fc52b6cea0744b2239921c5dcae4697f11
- https://github.com/Marynk/JavaScript-vulnerability-detection/blob/main/minimist%20PoC.zip
- https://github.com/minimistjs/minimist/commits/v0.2.4
- https://github.com/substack/minimist
- https://github.com/substack/minimist/blob/master/index.js#L69
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://snyk.io/vuln/SNYK-JS-MINIMIST-559764
- https://stackoverflow.com/questions/8588563/adding-custom-properties-to-a-function/20278068#20278068

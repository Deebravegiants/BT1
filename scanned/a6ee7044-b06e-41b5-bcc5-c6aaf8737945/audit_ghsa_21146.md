# [H] Regular expression denial of service in scss-tokenizer

## Summary
Severity: High
Advisory: GHSA-7mwh-4pqv-wmr8
CVE: CVE-2022-25758
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-02
Source: https://github.com/advisories/GHSA-7mwh-4pqv-wmr8
Type: github-advisory

## Affected
- npm: `scss-tokenizer` — affected >=0 <0.4.3

## Details
All versions of the package `scss-tokenizer` prior to 0.4.3 are vulnerable to Regular Expression Denial of Service (ReDoS) via the `loadAnnotation()` function, due to the usage of insecure regex.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25758
- https://github.com/sasstools/scss-tokenizer/issues/45
- https://github.com/sasstools/scss-tokenizer/pull/49
- https://github.com/sasstools/scss-tokenizer/commit/a53b6f233e648cc01acbdd89c58786cf8ba56e35
- https://github.com/sasstools/scss-tokenizer
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2936782
- https://snyk.io/vuln/SNYK-JS-SCSSTOKENIZER-2339884

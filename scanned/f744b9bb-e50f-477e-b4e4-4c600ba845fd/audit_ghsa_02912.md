# [H] Prototype Pollution via file load in aws-sdk and @aws-sdk/shared-ini-file-loader

## Summary
Severity: High
Advisory: GHSA-rrc9-gqf8-8rwg
CVE: CVE-2020-28472
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-11-16
Source: https://github.com/advisories/GHSA-rrc9-gqf8-8rwg
Type: github-advisory

## Affected
- npm: `aws-sdk` — affected >=0 <2.814.0
- npm: `@aws-sdk/shared-ini-file-loader` — affected >=0 <1.0.0-rc.9

## Details
This affects the package @aws-sdk/shared-ini-file-loader before 1.0.0-rc.9; the package aws-sdk before 2.814.0. If an attacker submits a malicious INI file to an application that parses it with loadSharedConfigFiles , they will pollute the prototype on the application. This can be exploited further depending on the context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28472
- https://github.com/aws/aws-sdk-js/pull/3585/commits/7d72aff2a941173733fcb6741b104cd83d3bc611
- https://github.com/aws/aws-sdk-js-v3/commit/a209082dff913939672bb069964b33aa4c5409a9
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1059426
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1059425
- https://snyk.io/vuln/SNYK-JS-AWSSDK-1059424
- https://snyk.io/vuln/SNYK-JS-AWSSDKSHAREDINIFILELOADER-1049304

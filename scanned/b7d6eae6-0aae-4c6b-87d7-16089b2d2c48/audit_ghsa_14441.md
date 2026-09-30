# [M] @nestjs/core vulnerable to Information Exposure via StreamableFile pipe

## Summary
Severity: Medium
Advisory: GHSA-4jpv-8r57-pv7j
CVE: CVE-2023-26108
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-06
Source: https://github.com/advisories/GHSA-4jpv-8r57-pv7j
Type: github-advisory

## Affected
- npm: `@nestjs/core` — affected >=0 <9.0.5

## Details
Versions of the package @nestjs/core before 9.0.5 are vulnerable to Information Exposure via the StreamableFile pipe. Exploiting this vulnerability is possible when the client cancels a request while it is streaming a StreamableFile, the stream wrapped by the StreamableFile will be kept open.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26108
- https://github.com/nestjs/nest/issues/9759
- https://github.com/nestjs/nest/pull/9819
- https://github.com/nestjs/nest/pull/9819/commits/f59cf5e81ca73bcdf1b5b36713550fd93918db41
- https://github.com/nestjs/nest
- https://security.snyk.io/vuln/SNYK-JS-NESTJSCORE-2869127

# [H] Prototype pollution in grpc and @grpc/grpc-js

## Summary
Severity: High
Advisory: GHSA-pp75-xfpw-37g9
CVE: CVE-2020-7768
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-pp75-xfpw-37g9
Type: github-advisory

## Affected
- npm: `grpc` — affected >=0 <1.24.4
- npm: `@grpc/grpc-js` — affected >=0 <1.1.8

## Details
"The package grpc before 1.24.4 and the package @grpc/grpc-js before 1.1.8 are vulnerable to Prototype Pollution via loadPackageDefinition."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7768
- https://github.com/grpc/grpc-node/pull/1605
- https://github.com/grpc/grpc-node/pull/1606
- https://github.com/grpc/grpc-node/releases/tag/grpc%401.24.4
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1038819
- https://snyk.io/vuln/SNYK-JS-GRPC-598671
- https://snyk.io/vuln/SNYK-JS-GRPCGRPCJS-1038818
- https://www.npmjs.com/package/@grpc/grpc-js
- https://www.npmjs.com/package/grpc

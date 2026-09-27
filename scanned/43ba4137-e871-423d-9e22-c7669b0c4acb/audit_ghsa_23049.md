# [H] Prototype Pollution in protobufjs

## Summary
Severity: High
Advisory: GHSA-g954-5hwp-pp24
CVE: CVE-2022-25878
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-28
Source: https://github.com/advisories/GHSA-g954-5hwp-pp24
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=6.11.0 <6.11.3
- npm: `protobufjs` — affected >=6.10.0 <6.10.3

## Details
The package protobufjs is vulnerable to Prototype Pollution, which can allow an attacker to add/modify properties of the Object.prototype. Versions after and including 6.10.0 until 6.10.3 and after and including 6.11.0 until 6.11.3 are vulnerable.

This vulnerability can occur in multiple ways:
1. by providing untrusted user input to util.setProperty or to ReflectionObject.setParsedOption functions
2. by parsing/loading .proto files

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25878
- https://github.com/protobufjs/protobuf.js/pull/1731
- https://github.com/protobufjs/protobuf.js/pull/1735
- https://github.com/protobufjs/protobuf.js/commit/b5f1391dff5515894830a6570e6d73f5511b2e8f
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/blob/d13d5d5688052e366aa2e9169f50dfca376b32cf/src/util.js%23L176-L197
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2841507
- https://snyk.io/vuln/SNYK-JS-PROTOBUFJS-2441248

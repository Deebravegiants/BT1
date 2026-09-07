# [C] protobufjs Prototype Pollution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h755-8qp9-cq85
CVE: CVE-2023-36665
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-h755-8qp9-cq85
Type: github-advisory

## Affected
- npm: `protobufjs` — affected >=7.0.0 <7.2.5
- npm: `protobufjs` — affected >=6.10.0 <6.11.4

## Details
protobuf.js (aka protobufjs) 6.10.0 until 6.11.4 and 7.0.0 until 7.2.4 allows Prototype Pollution, a different vulnerability than CVE-2022-25878. A user-controlled protobuf message can be used by an attacker to pollute the prototype of Object.prototype by adding and overwriting its data and functions. Exploitation can involve: (1) using the function parse to parse protobuf messages on the fly, (2) loading .proto files by using load/loadSync functions, or (3) providing untrusted input to the functions ReflectionObject.setParsedOption and util.setProperty. NOTE: this CVE Record is about `Object.constructor.prototype.<new-property> = ...;` whereas CVE-2022-25878 was about `Object.__proto__.<new-property> = ...;` instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36665
- https://github.com/protobufjs/protobuf.js/issues/1918#issuecomment-1723500294
- https://github.com/protobufjs/protobuf.js/pull/1899
- https://github.com/protobufjs/protobuf.js/commit/e66379f451b0393c27d87b37fa7d271619e16b0d
- https://github.com/protobufjs/protobuf.js
- https://github.com/protobufjs/protobuf.js/commits/release-6.11.4
- https://github.com/protobufjs/protobuf.js/compare/protobufjs-v7.2.3...protobufjs-v7.2.4
- https://github.com/protobufjs/protobuf.js/releases/tag/protobufjs-v7.2.4
- https://security.netapp.com/advisory/ntap-20240628-0006
- https://www.code-intelligence.com/blog/cve-protobufjs-prototype-pollution-cve-2023-36665

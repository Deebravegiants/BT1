# [C] Incorrect parsing of the backslash characters in Dart library

## Summary
Severity: Critical
Advisory: CVE-2022-3095
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-27
Source: https://osv.dev/vulnerability/CVE-2022-3095
Type: osv

## Details
The implementation of backslash parsing in the Dart URI class for versions prior to 2.18 and Flutter versions prior to 3.30 differs from the WhatWG URL standards. Dart uses the RFC 3986 syntax, which creates incompatibilities with the '\' characters in URIs, which can lead to auth bypass in webapps interpreting URIs. We recommend updating Dart or Flutter to mitigate the issue.

## References
- https://github.com/dart-lang/sdk/blob/master/CHANGELOG.md#2182---2022-09-28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3095.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3095

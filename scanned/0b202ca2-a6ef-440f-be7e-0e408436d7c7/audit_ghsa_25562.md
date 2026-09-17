# [M] URL Confusion When Scheme Not Supplied in medialize/uri.js

## Summary
Severity: Medium
Advisory: GHSA-g694-m8vq-gv9h
CVE: CVE-2022-1233
CWE: CWE-115, CWE-601
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-g694-m8vq-gv9h
Type: github-advisory

## Affected
- npm: `urijs` — affected >=0 <1.19.11

## Details
Medialize is a Javascript URL mutation library. When parsing a URL without a scheme and with excessive slashes, like ///www.example.com, URI.js will parse the hostname as null and the path as /www.example.com. Such behaviour is different from that exhibited by browsers, which will parse ///www.example.com as http://www.example.com instead. For example, the following will cause a redirect to http://www.example.com: A fix was released in version 1.19.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1233
- https://github.com/medialize/uri.js/commit/88805fd3da03bd7a5e60947adb49d182011f1277
- https://github.com/medialize/uri.js
- https://huntr.dev/bounties/228d5548-1109-49f8-8aee-91038e88371c

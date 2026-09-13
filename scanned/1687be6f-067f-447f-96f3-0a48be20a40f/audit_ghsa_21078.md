# [C] llhttp allows HTTP Request Smuggling via Flawed Parsing of Transfer-Encoding

## Summary
Severity: Critical
Advisory: GHSA-5689-v88g-g6rv
CVE: CVE-2022-32213
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-5689-v88g-g6rv
Type: github-advisory

## Affected
- npm: `llhttp` — affected >=0 <6.0.7

## Details
The llhttp parser in the http module in Node.js v17.x does not correctly parse and validate Transfer-Encoding headers and can lead to HTTP Request Smuggling (HRS).

Impacts:

- All versions of the nodejs 18.x, 16.x, and 14.x releases lines.
- llhttp v6.0.7 and llhttp v2.1.5 contains the fixes that were updated inside Node.js

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32213
- https://github.com/nodejs/llhttp/commit/18a4afc7ffb4e49dc9e2daebc50588199a6d1dbb
- https://hackerone.com/reports/1524555
- https://cert-portal.siemens.com/productcert/pdf/ssa-332410.pdf
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2ICG6CSIB3GUWH5DUSQEVX53MOJW7LYK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QCNN3YG2BCLS4ZEKJ3CLSUT6AS7AXTH3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VMQK5L5SBYD47QQZ67LEMHNQ662GH3OY
- https://nodejs.org/en/blog/vulnerability/july-2022-security-releases
- https://security.netapp.com/advisory/ntap-20220915-0001
- https://www.debian.org/security/2023/dsa-5326

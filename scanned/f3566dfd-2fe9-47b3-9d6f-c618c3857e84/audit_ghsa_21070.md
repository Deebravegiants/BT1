# [H] Apache SkyWalking NodeJS Agent can lose availability if header includes illegal SkyWalking header

## Summary
Severity: High
Advisory: GHSA-8gpg-466c-5cpj
CVE: CVE-2022-36127
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-19
Source: https://github.com/advisories/GHSA-8gpg-466c-5cpj
Type: github-advisory

## Affected
- npm: `skywalking-backend-js` — affected >=0 <0.5.1

## Details
A vulnerability in Apache SkyWalking NodeJS Agent prior to 0.5.1. The vulnerability will cause NodeJS services that has this agent installed to be unavailable if the OAP is unhealthy and NodeJS agent can't establish the connection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36127
- https://github.com/apache/skywalking-nodejs
- https://lists.apache.org/thread/x238wo4r5goy39dxdjcmlofp6gcdnqr3
- https://skywalking.apache.org/events/release-apache-skywalking-nodejs-0-5-1
- http://www.openwall.com/lists/oss-security/2022/07/18/1

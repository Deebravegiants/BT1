# [M] Machine-In-The-Middle in https-proxy-agent

## Summary
Severity: Medium
Advisory: GHSA-pc5p-h8pf-mvwp
CWE: CWE-300
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-16
Source: https://github.com/advisories/GHSA-pc5p-h8pf-mvwp
Type: github-advisory

## Affected
- npm: `https-proxy-agent` — affected >=0 <2.2.3

## Details
Versions of `https-proxy-agent` prior to 2.2.3 are vulnerable to Machine-In-The-Middle. The package fails to enforce TLS on the socket if the proxy server responds the to the request with a HTTP status different than 200. This allows an attacker with access to the proxy server to intercept unencrypted communications, which may include sensitive information such as credentials.


## Recommendation

Upgrade to version 3.0.0 or 2.2.3.

## References
- https://github.com/TooTallNate/node-https-proxy-agent/commit/36d8cf509f877fa44f4404fce57ebaf9410fe51b
- https://hackerone.com/reports/541502
- https://snyk.io/vuln/SNYK-JS-HTTPSPROXYAGENT-469131
- https://www.npmjs.com/advisories/1184

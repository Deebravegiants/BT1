# [M] amphp/http-server affected by HTTP/2 DDoS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8grv-jq2g-cfhw
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-8grv-jq2g-cfhw
Type: github-advisory

## Affected
- Packagist: `amphp/http-server` — affected >=3.0.0-beta.1 <3.4.4
- Packagist: `amphp/http-server` — affected >=2.0.0-rc1 <2.1.10

## Details
Versions of `amphp/http-server` prior to `3.4.4` for the 3.x release branch and prior to `2.1.10` for the 2.x release branch are vulnerable to the HTTP/2 "MadeYouReset" DoS attack described by CVE-2025-8671 and https://kb.cert.org/vuls/id/767506.

In versions `3.4.4` and `2.1.10`, stream reset protection has been refactored to account for the number of reset streams within a sliding time window.

Note that your application must expose HTTP/2 connections directly to be affected by this vulnerability. Servers behind a proxy using HTTP/1.x such as nginx are not affected.

## References
- https://github.com/amphp/http-server/security/advisories/GHSA-8grv-jq2g-cfhw
- https://github.com/amphp/http-server
- https://github.com/amphp/http-server/releases/tag/v2.1.10
- https://github.com/amphp/http-server/releases/tag/v3.4.4

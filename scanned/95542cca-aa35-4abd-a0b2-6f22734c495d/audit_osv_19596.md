# [H] CVE-2021-22568

## Summary
Severity: High
Advisory: CVE-2021-22568
Aliases: GHSA-r32f-vhjp-qhj7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L)
Published: 2021-12-09
Source: https://osv.dev/vulnerability/CVE-2021-22568
Type: osv

## Details
When using the dart pub publish command to publish a package to a third-party package server, the request would be authenticated with an oauth2 access_token that is valid for publishing on pub.dev. Using these obtained credentials, an attacker can impersonate the user on pub.dev. We recommend upgrading past https://github.com/dart-lang/sdk/commit/d787e78d21e12ec1ef712d229940b1172aafcdf8 or beyond version 2.15.0

## References
- https://github.com/dart-lang/sdk/security/advisories/GHSA-r32f-vhjp-qhj7
- https://github.com/dart-lang/sdk/blob/main/CHANGELOG.md
- https://github.com/dart-lang/sdk/commit/d787e78d21e12ec1ef712d229940b1172aafcdf8

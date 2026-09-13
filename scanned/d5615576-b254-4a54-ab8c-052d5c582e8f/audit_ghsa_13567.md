# [C] Code injection in fsevents

## Summary
Severity: Critical
Advisory: GHSA-8r6j-v8pm-fqw3
CVE: CVE-2023-45311
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-8r6j-v8pm-fqw3
Type: github-advisory

## Affected
- npm: `fsevents` — affected >=0 <1.2.11

## Details
fsevents before 1.2.11 depends on the https://fsevents-binaries.s3-us-west-2.amazonaws.com URL, which might allow an adversary to execute arbitrary code if any JavaScript project (that depends on fsevents) distributes code that was obtained from that URL at a time when it was controlled by an adversary.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45311
- https://github.com/fsevents/fsevents/commit/909af26846834642c81d19f4148afa3b7557b058
- https://github.com/atlassian/moo/blob/56ccbdd41b493332bc2cd7a4097a5802594cdb9c/package-lock.json#L1901-L1902
- https://github.com/atlassian/react-immutable-proptypes/blob/ddb9fa5194b931bf7528eb4f2c0a8c3434f70edd/package-lock.json#L153
- https://github.com/cloudflare/authr/blob/3f6129d97d06e61033a7f237d84e35e678db490f/ts/package-lock.json#L1512
- https://github.com/cloudflare/hugo-cloudflare-docs/blob/e0f7cfa195af8ef1bfa51a487be7d34ba298ed06/package-lock.json#L494
- https://github.com/cloudflare/redux-grim/blob/b652f99f95fb16812336073951adc5c5a93e2c23/package-lock.json#L266-L267
- https://github.com/cloudflare/serverless-cloudflare-workers/blob/e95e1e9c9770ed9a3d9480c1fa73e64391268354/package-lock.json#L737
- https://github.com/fsevents/fsevents
- https://github.com/fsevents/fsevents/compare/v1.2.10...v1.2.11
- https://security.snyk.io/vuln/SNYK-JS-FSEVENTS-5487987

# [H] Authentication bypass vulnerability in Apple Game Center auth adapter 

## Summary
Severity: High
Advisory: GHSA-rh9j-f5f8-rvgc
CVE: CVE-2022-31083
CWE: CWE-287, CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-rh9j-f5f8-rvgc
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.11
- npm: `parse-server` — affected >=5.0.0 <5.2.2

## Details
### Impact
The certificate in Apple Game Center auth adapter not validated. As a result, authentication could potentially be bypassed by making a fake certificate accessible via certain Apple domains and providing the URL to that certificate in an authData object.

### Patches
To prevent this, a new `rootCertificateUrl` property is introduced to the Parse Server Apple Game Center auth adapter which takes the URL to the root certificate of Apple's Game Center authentication certificate. If no value is set, the `rootCertificateUrl` property defaults to the URL of the [current root certificate](https://developer.apple.com/news/?id=stttq465) as of May 27, 2022.

Keep in mind that the root certificate can change at any time (expected to be announced by Apple) and that it is the developer's responsibility to keep the root certificate URL up-to-date when using the Parse Server Apple Game Center auth adapter.

### Workarounds
None.

### References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-rh9j-f5f8-rvgc
- https://developer.apple.com/news/?id=stttq465
- https://github.com/parse-community/parse-server

### More information
* For questions or comments about this vulnerability visit our [community forum](http://community.parseplatform.org) or [community chat](http://chat.parseplatform.org)
* Report other vulnerabilities at [report.parseplatform.org](https://report.parseplatform.org)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-rh9j-f5f8-rvgc
- https://nvd.nist.gov/vuln/detail/CVE-2022-31083
- https://github.com/parse-community/parse-server/pull/8054
- https://github.com/parse-community/parse-server/pull/8054/commits/0cc299f82e367518f2fe7a53b99f3f801a338cf4
- https://github.com/parse-community/parse-server/pull/8054/commits/2084b7c569697a5230e42511799eeac9219db5a9
- https://github.com/parse-community/parse-server/commit/ba2b0a9cb9a568817a114b132a4c2e0911d76df1
- https://developer.apple.com/news/?id=stttq465
- https://github.com/parse-community/parse-server

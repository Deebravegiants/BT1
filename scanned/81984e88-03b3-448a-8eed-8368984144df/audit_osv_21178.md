# [H] CVE-2021-41096

## Summary
Severity: High
Advisory: CVE-2021-41096
Aliases: GHSA-32m7-456v-wgfw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-27
Source: https://osv.dev/vulnerability/CVE-2021-41096
Type: osv

## Details
Rucky is a USB HID Rubber Ducky Launch Pad for Android. Versions 2.2 and earlier for release builds and versions 425 and earlier for nightly builds suffer from use of a weak cryptographic algorithm (RSA/ECB/PKCS1Padding). The issue will be patched in v2.3 for release builds and 426 onwards for nightly builds. As a workaround, one may disable an advance security feature if not required.

## References
- https://github.com/mayankmetha/Rucky/security/advisories/GHSA-32m7-456v-wgfw
- https://github.com/mayankmetha/Rucky/commit/5e3a477365009f488a73efd26a91168502de1b93

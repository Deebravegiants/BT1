# [M] CVE-2021-21288

## Summary
Severity: Medium
Advisory: CVE-2021-21288
Aliases: GHSA-fwcm-636p-68r5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-21288
Type: osv

## Details
CarrierWave is an open-source RubyGem which provides a simple and flexible way to upload files from Ruby applications. In CarrierWave before versions 1.3.2 and 2.1.1 the download feature has an SSRF vulnerability, allowing attacks to provide DNS entries or IP addresses that are intended for internal use and gather information about the Intranet infrastructure of the platform. This is fixed in versions 1.3.2 and 2.1.1.

## References
- https://github.com/carrierwaveuploader/carrierwave/blob/master/CHANGELOG.md#132---2021-02-08
- https://github.com/carrierwaveuploader/carrierwave/blob/master/CHANGELOG.md#211---2021-02-08
- https://github.com/carrierwaveuploader/carrierwave/security/advisories/GHSA-fwcm-636p-68r5
- https://rubygems.org/gems/carrierwave/
- https://github.com/carrierwaveuploader/carrierwave/commit/012702eb3ba1663452aa025831caa304d1a665c0

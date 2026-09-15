# [M] @fastly/js-compute has a use-after-free in some host call implementations

## Summary
Severity: Medium
Advisory: GHSA-mp3g-vpm9-9vqv
CVE: CVE-2024-38375
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-06-26
Source: https://github.com/advisories/GHSA-mp3g-vpm9-9vqv
Type: github-advisory

## Affected
- npm: `@fastly/js-compute` — affected >=3.0.0 <3.16.0

## Details
### Impact
The implementation of the following functions were determined to include a use-after-free bug:

* `FetchEvent.client.tlsCipherOpensslName`
* `FetchEvent.client.tlsProtocol`
* `FetchEvent.client.tlsClientCertificate`
* `FetchEvent.client.tlsJA3MD5`
* `FetchEvent.client.tlsClientHello`
* `CacheEntry.prototype.userMetadata` of the `fastly:cache` subsystem
* `Device.lookup` of the `fastly:device` subsystem

This bug could allow for an unintended data leak if the result of the preceding functions were sent anywhere else, and often results in a Compute service crash causing an HTTP 500 error to be returned. As all requests to Compute are isolated from one another, the only data at risk is data present for a single request.

### Patches
This bug has been fixed in version 3.16.0 of the `@fastly/js-compute` package.

### Workarounds
There are no workarounds for this bug, any use of the affected functions introduces the possibility of a data leak or crash in guest code.

## References
- https://github.com/fastly/js-compute-runtime/security/advisories/GHSA-mp3g-vpm9-9vqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-38375
- https://github.com/fastly/js-compute-runtime/commit/4e16641ef4e159c4a11b500ac861b8fa8d9ff5d3
- https://github.com/fastly/js-compute-runtime

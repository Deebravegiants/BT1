# [M] GeoIP processor disables SSL certificate validation when downloading databases

## Summary
Severity: Medium
Advisory: GHSA-3xgr-h5hq-7299
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-3xgr-h5hq-7299
Type: github-advisory

## Affected
- Maven: `org.opensearch.dataprepper.plugins:geoip-processor` — affected >=2.7.0 <2.12.2

## Details
### Impact

The GeoIP processor in Data Prepper was configured to trust all SSL certificates and disable hostname verification when downloading GeoIP databases from HTTP URLs, making downloads vulnerable to man-in-the-middle attacks.

The GeoIP processor included a custom SSL implementation that completely bypassed certificate validation when downloading GeoIP databases from external sources. The `initiateSSL()` method incorrectly implemented an approach for trusting all certificates. Specifically it:

* Accepted all SSL certificates without validation
* Disabled server certificate verification
* Disabled client certificate verification
* Disabled hostname verification

This configuration made database downloads vulnerable to man-in-the-middle attacks, potentially allowing attackers to serve malicious GeoIP databases that could compromise the integrity of geolocation data processing.

### Patches

Data Prepper 2.12.2 contains a fix for this issue.

### Workarounds

If upgrading is not immediately possible:

* Use local GeoIP database files instead of downloading from HTTP URLs
* Ensure database downloads occur only over trusted networks

## References
- https://github.com/opensearch-project/data-prepper/security/advisories/GHSA-3xgr-h5hq-7299
- https://github.com/opensearch-project/data-prepper/commit/b82ea0640d98d9f4c742622325faeeb6248ee135
- https://github.com/opensearch-project/data-prepper

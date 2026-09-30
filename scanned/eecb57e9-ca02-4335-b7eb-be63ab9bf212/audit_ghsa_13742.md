# [C] Json response for search reveals Solr credentials

## Summary
Severity: Critical
Advisory: GHSA-7crc-r3wg-cfgf
CWE: CWE-200
Ecosystem: Packagist
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-7crc-r3wg-cfgf
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-solr-search-engine` — affected >=3.3.0 <3.3.15
- Packagist: `ezsystems/ezplatform-solr-search-engine` — affected >=2.0.0 <2.0.2
- Packagist: `ezsystems/ezplatform-solr-search-engine` — affected >=1.7.0 <1.7.12

## Details
### Impact
An error in Ibexa's Solr search engine results in potential exposure of Solr credentials. This is a critical vulnerability and all supported versions of the engine are affected. Those not using the Solr search engine are not affected.

### Patches
The issue is fixed in all supported versions of ezsystems/ezplatform-solr-search-engine, see "Patched versions".
An advisory is also published for ibexa/solr, please see that repository.
Commit: https://github.com/ezsystems/ezplatform-solr-search-engine/commit/1005e02cc32ff15a705857fa56171528a83b9c3e

### Workarounds
None.

### References
https://developers.ibexa.co/security-advisories/ibexa-sa-2023-005-vulnerabilities-in-solr-search-and-file-downloads

## References
- https://github.com/ezsystems/ezplatform-solr-search-engine/security/advisories/GHSA-7crc-r3wg-cfgf
- https://github.com/ezsystems/ezplatform-solr-search-engine/commit/c382037208f38f18efb5a6b21d6936efc55fc408
- https://github.com/ezsystems/ezplatform-solr-search-engine

# [M] Element X iOS allows the entity in control of the well-known file to break the confidentiality of embedded Element Call

## Summary
Severity: Medium
Advisory: CVE-2025-31126
Aliases: GHSA-69qf-p24v-rf8j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-31126
Type: osv

## Details
Element X iOS is a Matrix iOS Client provided by Element. In Element X iOS version between 1.6.13 and 25.03.7, the entity in control of the element.json well-known file is able, under certain conditions, to get access to the media encryption keys used for an Element Call call. This vulnerability is fixed in 25.03.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31126.json
- https://github.com/element-hq/element-x-ios/security/advisories/GHSA-69qf-p24v-rf8j
- https://nvd.nist.gov/vuln/detail/CVE-2025-31126
- https://github.com/element-hq/element-meta/issues/2441

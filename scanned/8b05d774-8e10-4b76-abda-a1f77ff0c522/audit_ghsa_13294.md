# [M] Hard-coded System User Credentials in Folio Data Export Spring module 

## Summary
Severity: Medium
Advisory: GHSA-m8v7-469p-5x89
CVE: CVE-2024-23685
CWE: CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-m8v7-469p-5x89
Type: github-advisory

## Affected
- Maven: `org.folio:mod-remote-storage` — affected >=2.0.0 <2.0.3
- Maven: `org.folio:mod-remote-storage` — affected >=0 <1.7.2

## Details
### Impact
The module creates a system user that is used to perform internal module-to-module operations.  Credentials for this user are hard-coded in the source code.  This makes it trivial to authenticate as this user, allowing unauthorized read access to these mod-inventory-storage records: instances, holdings, items, contributor-types, identifier-types. This includes records marked as suppressed from discovery.

### Patches
Upgrade mod-remote-storage to >=2.0.3, or a 1.7.x version >=1.7.1.

### Workarounds
No known workarounds.

### References
https://wiki.folio.org/x/hbMMBw - FOLIO Security Advisory with Upgrade Instructions
https://github.com/folio-org/mod-remote-storage/commit/57df495f76e9aa5be9ce7ce3a65f89b6dbcbc13b - Fix

## References
- https://github.com/folio-org/mod-remote-storage/security/advisories/GHSA-m8v7-469p-5x89
- https://nvd.nist.gov/vuln/detail/CVE-2024-23685
- https://github.com/folio-org/mod-remote-storage/commit/57df495f76e9aa5be9ce7ce3a65f89b6dbcbc13b
- https://github.com/folio-org/mod-remote-storage
- https://vulncheck.com/advisories/vc-advisory-GHSA-m8v7-469p-5x89
- https://wiki.folio.org/x/hbMMBw

# [M] lsFusion Server is vulnerable to Path Traversal through its unpackFile function

## Summary
Severity: Medium
Advisory: GHSA-8wf8-frjg-xv74
CVE: CVE-2025-13265
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-8wf8-frjg-xv74
Type: github-advisory

## Affected
- Maven: `lsfusion.platform:server` — affected >=0

## Details
A weakness has been identified in lsfusion platform up to 6.1. This vulnerability affects the function unpackFile of the file server/src/main/java/lsfusion/server/physics/dev/integration/external/to/file/ZipUtils.java. This manipulation causes path traversal. It is possible to initiate the attack remotely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13265
- https://github.com/lsfusion/platform/issues/1545
- https://github.com/lsfusion/platform
- https://vuldb.com/?ctiid.332600
- https://vuldb.com/?id.332600
- https://vuldb.com/?submit.689427

# [M] The Altair Desktop Client Does Not Sanitize External URLs before passing them to the underlying system

## Summary
Severity: Medium
Advisory: CVE-2023-43799
Aliases: GHSA-9m5v-vrf6-fmvm
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-43799
Type: osv

## Details
Altair is a GraphQL Client. Prior to version 5.2.5, the Altair GraphQL Client Desktop Application does not sanitize external URLs before passing them to the underlying system. Moreover, Altair GraphQL Client also does not isolate the context of the renderer process. This affects versions of the software running on MacOS, Windows, and Linux. Version 5.2.5 fixes this issue.

## References
- https://github.com/altair-graphql/altair/releases/tag/v5.2.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43799.json
- https://github.com/altair-graphql/altair/security/advisories/GHSA-9m5v-vrf6-fmvm
- https://nvd.nist.gov/vuln/detail/CVE-2023-43799

# [M] Denial of service via Staff Actions in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-27100
Aliases: CVE-2024-27100, GHSA-xq4v-qg27-gxgc
Ecosystem: Bitnami
Published: 2024-04-01
Source: https://osv.dev/vulnerability/BIT-discourse-2024-27100
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.1

## Details
Discourse is an open source platform for community discussion. In affected versions the endpoints for suspending users, silencing users and exporting CSV files weren't enforcing limits on the sizes of the parameters that they accept. This could lead to excessive resource consumption which could render an instance inoperable. A site could be disrupted by either a malicious moderator on the same site or a malicious staff member on another site in the same multisite cluster. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/commit/8cade1e825e90a66f440e820992d43c6905f4b47
- https://github.com/discourse/discourse/security/advisories/GHSA-xq4v-qg27-gxgc
- https://nvd.nist.gov/vuln/detail/CVE-2024-27100

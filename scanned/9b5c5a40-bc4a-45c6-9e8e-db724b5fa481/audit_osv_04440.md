# [H] Denial of service by the absence of restrictions on replies to posts in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2024-43789
Aliases: CVE-2024-43789, GHSA-62cq-cpmc-hvqq
Ecosystem: Bitnami
Published: 2024-10-09
Source: https://osv.dev/vulnerability/BIT-discourse-2024-43789
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.1

## Details
Discourse is an open source platform for community discussion. A user can create a post with many replies, and then attempt to fetch them all at once. This can potentially reduce the availability of a Discourse instance. This problem has been patched in the latest version of Discourse. All users area are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-62cq-cpmc-hvqq
- https://nvd.nist.gov/vuln/detail/CVE-2024-43789

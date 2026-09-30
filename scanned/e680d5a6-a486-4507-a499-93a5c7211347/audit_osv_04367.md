# [M] Displaying user badges can leak topic titles to users that have no access to the topic

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-39378
Aliases: CVE-2022-39378, GHSA-2gvq-27h6-4h5f
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-39378
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.8.9

## Details
Discourse is a platform for community discussion. Under certain conditions, a user badge may have been awarded based on a user's activity in a topic with restricted access. Before this vulnerability was disclosed, the topic title of the topic associated with the user badge may be viewed by any user. If there are sensitive information in the topic title, it will therefore have been exposed. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. There are currently no known workarounds available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-2gvq-27h6-4h5f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39378

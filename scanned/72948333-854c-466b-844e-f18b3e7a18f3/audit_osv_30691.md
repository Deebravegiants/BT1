# [H] CVE-2024-55073

## Summary
Severity: High
Advisory: CVE-2024-55073
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2024-55073
Type: osv

## Details
A Broken Object Level Authorization vulnerability in the component /api/users/{user-id} of hay-kot mealie v2.2.0 allows users to edit their own profile in order to give themselves more permissions or to change their household.

## References
- https://m10x.de/posts/2025/03/all-your-recipe-are-belong-to-us-part-3/3-broken-access-controls-leading-to-privilege-escalation-and-more-in-mealie/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55073.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55073
- https://github.com/mealie-recipes/mealie/issues/4593

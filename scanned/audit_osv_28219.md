# [M] Pimcore Preview Documents are not restricted to logged in users anymore

## Summary
Severity: Medium
Advisory: CVE-2024-29197
Aliases: GHSA-5737-rqv4-v445
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-29197
Type: osv

## Details
Pimcore is an Open Source Data & Experience Management Platform. Any call with the query argument `?pimcore_preview=true` allows to view unpublished sites. In previous versions of Pimcore, session information would propagate to previews, so only a logged in user could open a preview. This no longer applies. Previews are broad open to any user and with just the hint of a restricted link one could gain access to possible confident / unreleased information. This vulnerability is fixed in 11.2.2 and 11.1.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29197.json
- https://github.com/pimcore/pimcore/security/advisories/GHSA-5737-rqv4-v445
- https://nvd.nist.gov/vuln/detail/CVE-2024-29197
- https://github.com/pimcore/pimcore/commit/3ae43fb1065f9eb62ad2f542b883858d36d57e53

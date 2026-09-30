# [C] Discourse Patreon vulnerable to improper validation of email during Patreon authentication

## Summary
Severity: Critical
Advisory: CVE-2022-39355
Aliases: GHSA-fvj9-f67v-qpr4
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-39355
Type: osv

## Details
Discourse Patreon enables syncronization between Discourse Groups and Patreon rewards. On sites with Patreon login enabled, an improper authentication vulnerability could be used to take control of a victim's forum account. This vulnerability is patched in commit number 846d012151514b35ce42a1636c7d70f6dcee879e of the discourse-patreon plugin. Out of an abundance of caution, any Discourse accounts which have logged in with an unverified-email Patreon account will be logged out and asked to verify their email address on their next login. As a workaround, disable the patreon integration and log out all users with associated Patreon accounts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39355.json
- https://github.com/discourse/discourse-patreon/security/advisories/GHSA-fvj9-f67v-qpr4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39355
- https://github.com/discourse/discourse-patreon/commit/846d012151514b35ce42a1636c7d70f6dcee879e

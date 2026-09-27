# [H] Camaleon CMS Insufficient Session Expiration vulnerability

## Summary
Severity: High
Advisory: GHSA-438x-2p9v-g8h9
CVE: CVE-2021-25970
CWE: CWE-613
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-438x-2p9v-g8h9
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=0.1.7 <2.6.0.1

## Details
Camaleon CMS 0.1.7 through 2.6.0 doesn’t terminate the active session of the users, even after the admin changes the user’s password. A user that was already logged in, will still have access to the application even after the password was changed. Resolved in commit `77e31bc6cdde7c951fba104aebcd5ebb3f02b030` which is included in the `2.6.0.1` release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25970
- https://github.com/owen2345/camaleon-cms/commit/77e31bc6cdde7c951fba104aebcd5ebb3f02b030
- https://github.com/owen2345/camaleon-cms
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2021-25970.yml
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25970

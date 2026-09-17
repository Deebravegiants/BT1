# [M] Publify `guest` role users can self-register even when the admin does not allow it

## Summary
Severity: Medium
Advisory: GHSA-x24j-87x9-jvv5
CVE: CVE-2021-25973
CWE: CWE-285, CWE-669, CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-x24j-87x9-jvv5
Type: github-advisory

## Affected
- RubyGems: `publify_core` — affected >=9.0.0.pre1 <9.2.5

## Details
In Publify, 9.0.0.pre1 to 9.2.4 are vulnerable to Improper Access Control. `guest` role users can self-register even when the admin does not allow it. This happens due to front-end restriction only.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25973
- https://github.com/publify/publify/commit/3447e0241e921b65f6eb1090453d8ea73e98387e
- https://github.com/publify/publify
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/publify_core/CVE-2021-25973.yml
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25973
